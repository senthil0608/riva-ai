// components/ParentDashboard.tsx
"use client";

import React, { useEffect, useState } from "react";

type ParentSummary = {
    summary_text: string;
    stress_level: string;
};

export default function ParentDashboard() {
    const [summary, setSummary] = useState<ParentSummary | null>(null);
    const [loading, setLoading] = useState(true);
    const [studentId, setStudentId] = useState("demo-student");

    useEffect(() => {
        const fetchSummary = async () => {
            setLoading(true);
            try {
                const res = await fetch("/api/aura", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        role: "parent",
                        action: "get_parent_summary",
                        studentId,
                    }),
                });
                const json = await res.json();
                setSummary(json?.parent_summary ?? null);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };

        fetchSummary();
    }, [studentId]);

    return (
        <div style={{ maxWidth: 800 }}>
            <div style={{ marginBottom: "1rem" }}>
                <label style={{ fontSize: "0.9rem", marginRight: "0.5rem" }}>
                    Student ID:
                </label>
                <input
                    value={studentId}
                    onChange={(e) => setStudentId(e.target.value)}
                    style={{
                        padding: "0.35rem 0.5rem",
                        borderRadius: 6,
                        border: "1px solid #4b5563",
                        background: "#020617",
                        color: "#f9fafb",
                    }}
                />
            </div>

            {loading && <p>Loading summary...</p>}

            {!loading && summary && (
                <div
                    style={{
                        border: "1px solid #374151",
                        borderRadius: 8,
                        padding: "1rem",
                    }}
                >
                    <h2 style={{ marginBottom: "0.5rem" }}>This Week at a Glance</h2>
                    <pre
                        style={{
                            whiteSpace: "pre-wrap",
                            fontSize: "0.95rem",
                            lineHeight: 1.5,
                        }}
                    >
                        {summary.summary_text}
                    </pre>
                    <div style={{ marginTop: "0.75rem", fontSize: "0.9rem" }}>
                        <strong>Stress Level:</strong> {summary.stress_level}
                    </div>
                </div>
            )}

            {!loading && !summary && <p>No summary available.</p>}
        </div>
    );
}
