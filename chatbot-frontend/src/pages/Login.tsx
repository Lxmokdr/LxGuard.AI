import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Lock, User, Key, AlertCircle, Sparkles } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!username || !password) {
            setError('Please enter both username and password');
            return;
        }

        const success = await login(username, password);
        if (success) {
            navigate('/');
        } else {
            setError('Invalid credentials. Please check your username and password.');
        }
    };

    const quickLogin = (user: 'admin' | 'employee' | 'guest') => {
        const credentials = {
            admin: { username: 'admin', password: 'admin123' },
            employee: { username: 'employee', password: 'employee123' },
            guest: { username: 'guest', password: 'guest123' },
        };

        setUsername(credentials[user].username);
        setPassword(credentials[user].password);
    };

    return (
        <div className="min-h-screen bg-background neural-bg flex items-center justify-center p-6">
            {/* Ambient glow effects */}
            <div className="fixed inset-0 pointer-events-none overflow-hidden">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-glow-cyan/5 rounded-full blur-3xl" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-glow-emerald/5 rounded-full blur-3xl" />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="relative z-10 w-full max-w-md"
            >
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary/10 glow-border-cyan mb-4">
                        <Lock className="w-8 h-8 text-primary" />
                    </div>
                    <h1 className="text-3xl font-bold text-foreground mb-2">
                        Hybrid Knowledge Agent
                    </h1>
                    <p className="text-sm text-muted-foreground">
                        Sign in to access the intelligent chatbot
                    </p>
                </div>

                {/* Login Form */}
                <div className="glass-card p-8">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Username */}
                        <div className="space-y-2">
                            <Label htmlFor="username" className="text-sm font-medium">
                                Username
                            </Label>
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                                <Input
                                    id="username"
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    placeholder="Enter your username"
                                    className="pl-10 bg-muted/50 border-border/50 focus:border-primary/50"
                                />
                            </div>
                        </div>

                        {/* Password */}
                        <div className="space-y-2">
                            <Label htmlFor="password" className="text-sm font-medium">
                                Password
                            </Label>
                            <div className="relative">
                                <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                                <Input
                                    id="password"
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className="pl-10 bg-muted/50 border-border/50 focus:border-primary/50"
                                />
                            </div>
                        </div>

                        {/* Error Message */}
                        {error && (
                            <Alert variant="destructive" className="bg-destructive/10 border-destructive/30">
                                <AlertCircle className="h-4 w-4" />
                                <AlertDescription>{error}</AlertDescription>
                            </Alert>
                        )}

                        {/* Submit Button */}
                        <Button
                            type="submit"
                            className="w-full bg-primary text-primary-foreground glow-border-cyan"
                        >
                            <Lock className="w-4 h-4 mr-2" />
                            Sign In
                        </Button>
                    </form>

                    {/* Quick Login Options */}
                    <div className="mt-8 pt-6 border-t border-border/50">
                        <p className="text-xs text-muted-foreground mb-3 flex items-center gap-2">
                            <Sparkles className="w-3 h-3" />
                            Quick Login (Demo)
                        </p>
                        <div className="grid grid-cols-3 gap-2">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => quickLogin('admin')}
                                className="text-xs border-blue-500/30 hover:bg-blue-500/10"
                            >
                                Admin
                            </Button>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => quickLogin('employee')}
                                className="text-xs border-green-500/30 hover:bg-green-500/10"
                            >
                                Employee
                            </Button>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => quickLogin('guest')}
                                className="text-xs border-purple-500/30 hover:bg-purple-500/10"
                            >
                                Guest
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Credentials Info */}
                <div className="mt-6 glass-card p-4">
                    <p className="text-xs text-muted-foreground mb-2 font-semibold">Demo Credentials:</p>
                    <div className="space-y-1 text-xs font-mono text-muted-foreground">
                        <div>🔵 <span className="text-blue-400">admin</span> / admin123</div>
                        <div>🟢 <span className="text-green-400">employee</span> / employee123</div>
                        <div>🟣 <span className="text-purple-400">guest</span> / guest123</div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default Login;
