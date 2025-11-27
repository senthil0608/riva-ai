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
    due?: string;
};

type AuraResponse = {
    assignments: Assignment[];
    daily_plan: PlanItem[];
};

export default function StudentDashboard() {
    const [data, setData] = useState<AuraResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [pastDueDays, setPastDueDays] = useState(30);
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

    // Helper to check if date is > pastDueDays old
    const isOld = (dateStr?: string) => {
        if (!dateStr || dateStr === "No due date") return false;
        const due = new Date(dateStr);
        const today = new Date();
        const diffTime = today.getTime() - due.getTime();
        const diffDays = diffTime / (1000 * 3600 * 24);
        return diffDays > pastDueDays;
    };

    const currentAssignments = data?.assignments?.filter((a) => !isOld(a.due)) || [];
    const oldAssignments = data?.assignments?.filter((a) => isOld(a.due)) || [];

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
                                {item.subject} • {item.difficulty_tag} {item.due ? `• Due ${item.due}` : ""}
                            </div>
                        </div>
                    ))}

                <h3 style={{ marginTop: "1.5rem", marginBottom: "0.5rem" }}>
                    Current Assignments
                </h3>
                {!loading &&
                    currentAssignments.map((a) => (
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

                <div style={{ marginTop: "2rem" }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                        <h3 style={{ fontSize: "1.1rem", color: "#9CA3AF", margin: 0 }}>
                            Past Due
                        </h3>
                        <div style={{ fontSize: "0.85rem", color: "#9CA3AF" }}>
                            {"> "}
                            <input
                                type="number"
                                value={pastDueDays}
                                onChange={(e) => setPastDueDays(Number(e.target.value))}
                                style={{
                                    width: "3rem",
                                    background: "#1F2937",
                                    border: "1px solid #374151",
                                    color: "white",
                                    borderRadius: "4px",
                                    padding: "0.1rem 0.3rem",
                                    textAlign: "center"
                                }}
                            />
                            {" days"}
                        </div>
                    </div>

                    {oldAssignments.length === 0 && (
                        <p style={{ fontSize: "0.85rem", color: "#6B7280" }}>No assignments found.</p>
                    )}

                    {oldAssignments.map((a) => (
                        <div
                            key={a.id}
                            style={{
                                borderBottom: "1px solid #374151",
                                padding: "0.5rem 0",
                                opacity: 0.6,
                            }}
                        >
                            <div style={{ fontWeight: 500, fontSize: "0.9rem" }}>{a.title}</div>
                            <div style={{ fontSize: "0.8rem" }}>
                                {a.subject} • Due {a.due}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
