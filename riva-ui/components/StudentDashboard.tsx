// components/StudentDashboard.tsx
"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import HintPanel from "./HintPanel";

type Assignment = {
    id: string;
    title: string;
    subject: string;
    due?: string;
    state?: string;
};

type PlanItem = {
    time: string;
    task_id: string;
    title: string;
    subject: string;
    difficulty_tag: string;
    due?: string;
    state?: string;
};

type AuraResponse = {
    assignments: Assignment[];
    daily_plan: PlanItem[];
};

export default function StudentDashboard() {
    const router = useRouter(); // Added router initialization
    const [studentId, setStudentId] = useState<string>(""); // Changed initial value and type
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<any>(null); // Changed type to any as per instruction
    const [pastDueDays, setPastDueDays] = useState(7);
    const [userToken, setUserToken] = useState<string>("");

    // Check user status and get token on mount
    useEffect(() => {
        const initAuth = async () => {
            // Wait for firebase auth to initialize
            // We can use onAuthStateChanged
            const { onAuthStateChanged } = await import("firebase/auth"); // Dynamic import to avoid SSR issues if any
            const { auth } = await import("../lib/firebaseConfig");

            const unsubscribe = onAuthStateChanged(auth, async (user) => {
                if (user) {
                    const token = await user.getIdToken();
                    setUserToken(token);

                    // Also check if configured (optional, but good for consistency)
                    try {
                        const res = await fetch("/api/user");
                        const json = await res.json();
                        if (!json.configured) {
                            router.push("/onboarding");
                        } else {
                            setStudentId(json.user.student_emails[0]);
                        }
                    } catch (e) {
                        console.error(e);
                    }

                } else {
                    // Not logged in, redirect to login
                    router.push("/");
                }
            });
            return () => unsubscribe();
        };
        initAuth();
    }, [router]);

    useEffect(() => {
        if (!studentId || !userToken) return; // Wait for both

        const fetchData = async () => {
            setLoading(true);
            try {
                const res = await fetch("/api/aura", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${userToken}`,
                        "X-Authorization": `Bearer ${userToken}` // Fallback for proxy stripping
                    },
                    body: JSON.stringify({
                        role: "student",
                        action: "get_dashboard",
                        studentId,
                        auth_token: userToken, // Fallback for aggressive header stripping
                    }),
                });
                const json = await res.json();
                if (json.error) { // Added error handling
                    console.error(json.error);
                    if (json.error.includes("Access denied") || json.error.includes("Invalid token")) {
                        router.push("/"); // Redirect to login on auth error
                    }
                } else {
                    setData(json);
                }
            } catch (err) {
                console.error("Failed to fetch Aura data", err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [studentId, userToken]);

    // Helper to check if date is > pastDueDays old
    const isOld = (dateStr?: string) => {
        if (!dateStr || dateStr === "No due date") return false;
        const due = new Date(dateStr);
        const today = new Date();
        const diffTime = today.getTime() - due.getTime();
        const diffDays = diffTime / (1000 * 3600 * 24);
        return diffDays > pastDueDays;
    };

    const hasNoDueDate = (a: Assignment) => !a.due || a.due === "No due date";

    const getAssignmentColor = (a: Assignment | PlanItem) => {
        // Green: Completed
        if (a.state === 'TURNED_IN' || a.state === 'RETURNED') {
            return '#22c55e'; // Green-500
        }

        if (!a.due || a.due === "No due date") {
            return '#eab308'; // Yellow-500 (Treat no due date as low risk/future)
        }

        const due = new Date(a.due);
        const today = new Date();
        today.setHours(0, 0, 0, 0); // Normalize today to start of day

        // Check if strictly past due (yesterday or earlier)
        // We add 1 day (86400000ms) to due date to compare with today effectively? 
        // Actually, simple comparison: if due < today (midnight), it's past due.
        // But due dates from classroom might be just YYYY-MM-DD.
        // Let's assume due date is end of that day.
        const dueEndOfDay = new Date(due);
        dueEndOfDay.setHours(23, 59, 59, 999);

        if (dueEndOfDay < today) {
            return '#ef4444'; // Red-500 (Cannot be completed / Past Due)
        }

        // Orange: Due Today or Tomorrow
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        tomorrow.setHours(23, 59, 59, 999);

        if (dueEndOfDay <= tomorrow) {
            return '#f97316'; // Orange-500 (Verge of not completing)
        }

        // Yellow: Future
        return '#eab308'; // Yellow-500 (No risk yet)
    };

    const currentAssignments = data?.assignments?.filter((a: Assignment) => !isOld(a.due) && !hasNoDueDate(a)) || [];
    const noDueAssignments = data?.assignments?.filter((a: Assignment) => hasNoDueDate(a)) || [];
    const oldAssignments = data?.assignments?.filter((a: Assignment) => isOld(a.due)) || [];

    return (
        <div style={{ display: "grid", gap: "1.5rem", gridTemplateColumns: "2fr 1.5fr" }}>
            <div>
                <h2 style={{ marginBottom: "0.5rem" }}>Today&apos;s Plan</h2>
                {loading && <p>Loading plan...</p>}
                {!loading && data && data.daily_plan?.length === 0 && (
                    <p>No tasks planned for today.</p>
                )}
                {!loading &&
                    data?.daily_plan?.map((item: PlanItem) => (
                        <div
                            key={item.task_id}
                            style={{
                                border: "1px solid #374151",
                                borderRadius: 8,
                                padding: "0.75rem 1rem",
                                marginBottom: "0.5rem",
                            }}
                        >
                            <div style={{ fontWeight: 600, color: getAssignmentColor(item) }}>
                                {item.time} – {item.title}
                            </div>
                            <div style={{ fontSize: "0.85rem", opacity: 0.8 }}>
                                {item.subject} • {item.difficulty_tag} {item.due ? `• Due ${item.due}` : ""}
                            </div>
                        </div>
                    ))}

                <h3 style={{ marginTop: "2rem", marginBottom: "0.5rem" }}>
                    Current Assignments
                </h3>
                {!loading &&
                    currentAssignments.map((a: Assignment) => (
                        <div
                            key={a.id}
                            style={{
                                borderBottom: "1px solid #111827",
                                padding: "0.5rem 0",
                            }}
                        >
                            <div style={{ fontWeight: 500, color: getAssignmentColor(a) }}>{a.title}</div>
                            <div style={{ fontSize: "0.85rem", opacity: 0.8 }}>
                                {a.subject} {a.due ? `• Due ${a.due}` : ""}
                            </div>
                        </div>
                    ))}

                {noDueAssignments.length > 0 && (
                    <>
                        <h3 style={{ marginTop: "2rem", marginBottom: "0.5rem" }}>
                            No Due Date
                        </h3>
                        {!loading &&
                            noDueAssignments.map((a: Assignment) => (
                                <div
                                    key={a.id}
                                    style={{
                                        borderBottom: "1px solid #111827",
                                        padding: "0.5rem 0",
                                    }}
                                >
                                    <div style={{ fontWeight: 500, color: getAssignmentColor(a) }}>{a.title}</div>
                                    <div style={{ fontSize: "0.85rem", opacity: 0.8 }}>
                                        {a.subject}
                                    </div>
                                </div>
                            ))}
                    </>
                )}
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

                    {oldAssignments.map((a: Assignment) => (
                        <div
                            key={a.id}
                            style={{
                                borderBottom: "1px solid #374151",
                                padding: "0.5rem 0",
                                opacity: 0.6,
                            }}
                        >
                            <div style={{ fontWeight: 500, fontSize: "0.9rem", color: getAssignmentColor(a) }}>{a.title}</div>
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
