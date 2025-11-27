// components/HintPanel.tsx
"use client";

import React, { useState } from "react";

export default function HintPanel() {
    const [hint, setHint] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const handleAskHint = async () => {
        setLoading(true);
        setHint(null);
        try {
            const res = await fetch("/api/aura", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    role: "student",
                    action: "guided_hint",
                    // In future: include image/audio IDs or text of problem
                    question: "example problem text from UI",
                }),
            });
            const json = await res.json();
            setHint(json?.hint ?? "No hint returned.");
        } catch (e) {
            console.error(e);
            setHint("Sorry, I couldn't fetch a hint.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div
            style={{
                border: "1px solid #374151",
                borderRadius: 8,
                padding: "1rem",
            }}
        >
            <h3 style={{ marginBottom: "0.5rem" }}>Need a hint?</h3>
            <p style={{ fontSize: "0.9rem", opacity: 0.9, marginBottom: "1rem" }}>
                Upload a photo or describe the problem, and Aura will guide you with
                steps—not the full answer.
            </p>

            {/* Future: file upload + voice record buttons */}
            <button
                onClick={handleAskHint}
                disabled={loading}
                style={{
                    padding: "0.5rem 1rem",
                    borderRadius: 999,
                    border: "none",
                    background: "#2563eb",
                    color: "white",
                    cursor: "pointer",
                }}
            >
                {loading ? "Thinking..." : "Ask for a Hint"}
            </button>

            {hint && (
                <div
                    style={{
                        marginTop: "1rem",
                        padding: "0.75rem",
                        borderRadius: 8,
                        background: "#111827",
                        fontSize: "0.9rem",
                    }}
                >
                    {hint}
                </div>
            )}
        </div>
    );
}
