import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "LxGuard.AI — Multi-Layer AI Governance",
    description: "Secure • Explainable • Enterprise AI — Animated System Explainer",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en" className="dark">
            <body className="min-h-screen bg-[#0a0b1a] text-white antialiased" style={{ fontFamily: "'Inter', system-ui, sans-serif" }}>
                {children}
            </body>
        </html>
    );
}
