// app/page.tsx
"use client";

import Link from "next/link";

export default function HomePage() {
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

            <div
                style={{
                    display: "flex",
                    gap: "1.5rem",
                    justifyContent: "center",
                    flexWrap: "wrap",
                }}
            >
                <Link
                    href="/student"
                    style={{
                        padding: "1rem 1.5rem",
                        borderRadius: 8,
                        border: "1px solid #374151",
                        textDecoration: "none",
                    }}
                >
                    I&apos;m a Student
                </Link>

                <Link
                    href="/parent"
                    style={{
                        padding: "1rem 1.5rem",
                        borderRadius: 8,
                        border: "1px solid #374151",
                        textDecoration: "none",
                    }}
                >
                    I&apos;m a Parent
                </Link>
            </div>
        </div>
    );
}
