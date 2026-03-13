'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { adminApi } from '@/lib/api';

interface User {
    username: string;
    role: string;
}

interface AuthContextType {
    user: User | null;
    login: (credentials: FormData) => Promise<void>;
    logout: () => void;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        let isMounted = true;

        const initAuth = async () => {
            const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
            if (token && pathname !== '/login') {
                try {
                    const userData = await adminApi.auth.me();
                    if (isMounted) {
                        setUser(userData);
                    }
                } catch (error) {
                    console.error("Auth init failed", error);
                    if (isMounted) {
                        localStorage.removeItem('access_token');
                        localStorage.removeItem('user');
                        if (pathname !== '/login') router.push('/login');
                    }
                }
            } else if (!token && pathname !== '/login') {
                if (isMounted) router.push('/login');
            }
            if (isMounted) {
                setIsLoading(false);
            }
        };

        initAuth();

        return () => {
            isMounted = false;
        };
    }, [pathname, router]);

    const login = useCallback(async (credentials: FormData) => {
        try {
            const data = await adminApi.auth.login(credentials);
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user', JSON.stringify({ username: data.username, role: data.role }));

            if (data.role !== 'admin') {
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                throw new Error("Access denied: Admin role required");
            }

            setUser({ username: data.username, role: data.role });
            router.push('/dashboard');
        } catch (error: any) {
            throw error;
        }
    }, [router]);

    const logout = useCallback(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        setUser(null);
        router.push('/login');
    }, [router]);

    return (
        <AuthContext.Provider value={{ user, login, logout, isLoading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
