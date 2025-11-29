// app/page.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { signInWithPopup } from "firebase/auth";
import { auth, googleProvider } from "../lib/firebaseConfig";

export default function HomePage() {
    const router = useRouter();
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleLogin = async (role: "student" | "parent") => {
        setLoading(true);
        setError("");
        try {
            const result = await signInWithPopup(auth, googleProvider);
            const user = result.user;
            const token = await user.getIdToken();

            // Verify with backend
            const res = await fetch("/api/auth/verify", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ role })
            });

            const json = await res.json();

            if (res.ok && json.status === "success") {
                // Redirect to appropriate dashboard
                router.push(`/${role}`);
            } else {
                setError(json.error || "Authentication failed");
                // Optional: Sign out from Firebase if backend rejects
                await auth.signOut();
            }
        } catch (err: any) {
            console.error("Login error:", err);
            setError(err.message || "Failed to sign in");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div
            style={{
                maxWidth: 800,
                margin: "0 auto",
                textAlign: "center",
                marginTop: "3rem",
            }}
        >
            <h1 style={{ fontSize: "2rem", marginBottom: "1rem" }}>
                Welcome to Riva.ai – Academic Coach
            </h1>
            <p style={{ opacity: 0.8, marginBottom: "2rem" }}>
                Aura aligns homework, schedules, and learning priorities for students
                and families.
            </p>

            {error && (
                <div style={{
                    color: "#ef4444",
                    marginBottom: "1rem",
                    padding: "0.5rem",
                    border: "1px solid #ef4444",
                    borderRadius: "4px",
                    display: "inline-block"
                }}>
                    {error}
                </div>
            )}

            <div
                style={{
                    display: "flex",
                    gap: "1.5rem",
                    justifyContent: "center",
                    flexWrap: "wrap",
                }}
            >
                <button
                    onClick={() => handleLogin("student")}
                    disabled={loading}
                    style={{
                        padding: "1rem 1.5rem",
                        borderRadius: 8,
                        border: "1px solid #374151",
                        background: "transparent",
                        color: "white",
                        cursor: "pointer",
                        fontSize: "1rem"
                    }}
                >
                    {loading ? "Signing in..." : "Student Login"}
                </button>

                <button
                    onClick={() => handleLogin("parent")}
                    disabled={loading}
                    style={{
                        padding: "1rem 1.5rem",
                        borderRadius: 8,
                        border: "1px solid #374151",
                        background: "transparent",
                        color: "white",
                        cursor: "pointer",
                        fontSize: "1rem"
                    }}
                >
                    {loading ? "Signing in..." : "Parent Login"}
                </button>
            </div>

            <div style={{ marginTop: "2rem", opacity: 0.6, fontSize: "0.9rem" }}>
                <p>First time here? <a href="/onboarding" style={{ color: "#60a5fa" }}>Setup your account</a></p>
            </div>
        </div>
    );
}
