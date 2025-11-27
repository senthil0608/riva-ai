// app/layout.tsx
import "./globals.css";
import React from "react";

export const metadata = {
    title: "Riva.ai – Academic Coach",
    description: "Aura-powered academic coach for students and parents",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body
                style={{
                    margin: 0,
                    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
                    background: "#050816",
                    color: "#f9fafb",
                }}
            >
                <header
                    style={{
                        padding: "1rem 2rem",
                        borderBottom: "1px solid #1f2933",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                    }}
                >
                    <div style={{ fontWeight: 700, fontSize: "1.25rem" }}>Riva.ai</div>
                    <div style={{ fontSize: "0.9rem", opacity: 0.8 }}>
                        Aura – Learning–Life Harmony
                    </div>
                </header>
                <main
                    style={{
                        padding: "1.5rem 2rem",
                        minHeight: "calc(100vh - 64px)",
                    }}
                >
                    {children}
                </main>
            </body>
        </html>
    );
}
