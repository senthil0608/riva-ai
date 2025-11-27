// components/StudentDashboard.tsx
"use client";

import React, { useEffect, useState } from "react";
import HintPanel from "./HintPanel";

type Assignment = {
    id: string;
    title: string;
    subject: string;
    due?: string;
};

type PlanItem = {
    time: string;
    task_id: string;
    title: string;
    subject: string;
    difficulty_tag: string;
};

type AuraResponse = {
    assignments: Assignment[];
    daily_plan: PlanItem[];
};

export default function StudentDashboard() {
    const [data, setData] = useState<AuraResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [studentId, setStudentId] = useState("demo-student");

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const res = await fetch("/api/aura", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        role: "student",
                        action: "get_dashboard",
                        studentId,
                    }),
                });
                const json = await res.json();
                setData(json);
            } catch (err) {
                console.error("Failed to fetch Aura data", err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [studentId]);

    return (
        <div style={{ display: "grid", gap: "1.5rem", gridTemplateColumns: "2fr 1.5fr" }}>
            <div>
                <h2 style={{ marginBottom: "0.5rem" }}>Today&apos;s Plan</h2>
                {loading && <p>Loading plan...</p>}
                {!loading && data && data.daily_plan?.length === 0 && (
                    <p>No tasks planned for today.</p>
                )}
                {!loading &&
                    data?.daily_plan?.map((item) => (
                        <div
                            key={item.task_id}
                            style={{
                                border: "1px solid #374151",
                                borderRadius: 8,
                                padding: "0.75rem 1rem",
                                marginBottom: "0.5rem",
                            }}
                        >
                            <div style={{ fontWeight: 600 }}>
                                {item.time} – {item.title}
                            </div>
                            <div style={{ fontSize: "0.85rem", opacity: 0.8 }}>
                                {item.subject} • {item.difficulty_tag}
                            </div>
                        </div>
                    ))}

                <h3 style={{ marginTop: "1.5rem", marginBottom: "0.5rem" }}>
                    All Assignments
                </h3>
                {!loading &&
                    data?.assignments?.map((a) => (
                        <div
                            key={a.id}
                            style={{
                                borderBottom: "1px solid #111827",
                                padding: "0.5rem 0",
                            }}
                        >
                            <div style={{ fontWeight: 500 }}>{a.title}</div>
                            <div style={{ fontSize: "0.85rem", opacity: 0.8 }}>
                                {a.subject} {a.due ? `• Due ${a.due}` : ""}
                            </div>
                        </div>
                    ))}
            </div>

            <div>
                <HintPanel />
            </div>
        </div>
    );
}
