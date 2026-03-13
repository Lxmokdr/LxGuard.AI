'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Lock, User, AlertCircle } from 'lucide-react';

export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        try {
            await login(formData);
        } catch (err: any) {
            setError(err.message || 'Login failed. Please check your credentials.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-zinc-950 p-4">
            <div className="w-full max-w-md">
                <div className="flex justify-center mb-8">
                    <div className="bg-indigo-600 p-3 rounded-xl shadow-lg shadow-indigo-500/20">
                        <Lock className="w-8 h-8 text-white" />
                    </div>
                </div>

                <Card className="border-zinc-800 bg-zinc-900 shadow-2xl">
                    <CardHeader className="space-y-1 text-center">
                        <CardTitle className="text-2xl font-bold text-white uppercase tracking-wider">Admin Portal</CardTitle>
                        <CardDescription className="text-zinc-400">
                            Enter your credentials to access the management dashboard
                        </CardDescription>
                    </CardHeader>
                    <form onSubmit={handleSubmit}>
                        <CardContent className="space-y-4 pt-4">
                            {error && (
                                <div className="bg-red-500/10 border border-red-500/50 p-3 rounded-lg flex items-center gap-3 text-red-500 text-sm">
                                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                                    <p>{error}</p>
                                </div>
                            )}

                            <div className="space-y-2">
                                <Label htmlFor="username" className="text-zinc-300">Username</Label>
                                <div className="relative">
                                    <User className="absolute left-3 top-3 w-4 h-4 text-zinc-500" />
                                    <Input
                                        id="username"
                                        placeholder="admin"
                                        className="pl-10 bg-zinc-950 border-zinc-800 text-white focus:ring-indigo-500 focus:border-indigo-500"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="password" className="text-zinc-300">Password</Label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-3 w-4 h-4 text-zinc-500" />
                                    <Input
                                        id="password"
                                        type="password"
                                        placeholder="••••••••"
                                        className="pl-10 bg-zinc-950 border-zinc-800 text-white focus:ring-indigo-500 focus:border-indigo-500"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>
                        </CardContent>
                        <CardFooter className="pt-4 flex flex-col gap-4">
                            <Button
                                type="submit"
                                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-6"
                                disabled={isLoading}
                            >
                                {isLoading ? 'Authenticating...' : 'Sign In'}
                            </Button>

                            <div className="text-center text-xs text-zinc-500">
                                <p>Default: admin / admin123</p>
                            </div>
                        </CardFooter>
                    </form>
                </Card>
            </div>
        </div>
    );
}
