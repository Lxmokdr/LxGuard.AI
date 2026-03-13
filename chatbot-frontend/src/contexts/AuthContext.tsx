import React, { createContext, useContext, useState, useEffect } from 'react';
import { API_URL } from "../config";

export interface User {
    username: string;
    role: 'admin' | 'employee' | 'guest';
}

interface AuthContextType {
    user: User | null;
    login: (username: string, password: string) => Promise<boolean>;
    logout: () => void;
    isAuthenticated: boolean;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Load user from localStorage on mount and check token
    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem('access_token');
            const storedUser = localStorage.getItem('user');
            const expiresAt = localStorage.getItem('expiresAt');

            // Check if 1 hour has passed
            if (expiresAt && Date.now() > parseInt(expiresAt)) {
                logout();
                setIsLoading(false);
                return;
            }

            if (token && storedUser) {
                try {
                    // Check if session is still valid
                    const res = await fetch(`${API_URL}/auth/me`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });

                    if (res.ok) {
                        setUser(JSON.parse(storedUser));
                    } else {
                        logout();
                    }
                } catch (e) {
                    console.error("Auth check failed", e);
                    logout();
                }
            }
            setIsLoading(false);
        };
        checkAuth();
    }, []);

    const login = async (username: string, password: string): Promise<boolean> => {
        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const res = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                body: formData
            });

            if (res.ok) {
                const data = await res.json();
                const newUser: User = { username: data.username, role: data.role };
                setUser(newUser);
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('user', JSON.stringify(newUser));

                // Add 1 hour expiration explicitly
                const expiresAt = Date.now() + 60 * 60 * 1000;
                localStorage.setItem('expiresAt', expiresAt.toString());

                return true;
            }
            return false;
        } catch (e) {
            console.error("Login failed", e);
            return false;
        }
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        localStorage.removeItem('expiresAt');
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user, isLoading }}>
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
