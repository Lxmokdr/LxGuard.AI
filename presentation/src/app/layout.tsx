import "./globals.css";

export const metadata = {
    title: "Hybrid NLP-Expert Agent Presentation",
    description: "Complete System Overview",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className="min-h-screen bg-black text-white antialiased">
                {children}
            </body>
        </html>
    );
}
