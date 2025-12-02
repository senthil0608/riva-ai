// components/StudentDashboard.tsx
"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Calendar, List, Clock } from "lucide-react";
import AuraInput from "./AuraInput";
import DashboardColumn from "./DashboardColumn";
import CollapsibleSection from "./CollapsibleSection";
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

const SkeletonCard = () => (
    <div className="mb-3 p-3 rounded-lg bg-white/5 border border-white/10 animate-pulse">
        <div className="flex justify-between items-start mb-2">
            <div className="h-4 bg-white/10 rounded w-1/3"></div>
            <div className="h-4 bg-white/10 rounded w-1/4"></div>
        </div>
        <div className="h-4 bg-white/10 rounded w-3/4 mb-2"></div>
        <div className="h-3 bg-white/10 rounded w-1/2"></div>
    </div>
);

export default function StudentDashboard() {
    const router = useRouter();
    const [studentId, setStudentId] = useState<string>("");
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<any>(null);
    const [pastDueDays, setPastDueDays] = useState(7);
    const [userToken, setUserToken] = useState<string>("");
    const [isProcessing, setIsProcessing] = useState(false);

    const [error, setError] = useState<string | null>(null);

    // Check user status and get token on mount
    useEffect(() => {
        const initAuth = async () => {
            const { onAuthStateChanged } = await import("firebase/auth");
            const { auth } = await import("../lib/firebaseConfig");

            const unsubscribe = onAuthStateChanged(auth, async (user) => {
                if (user) {
                    const token = await user.getIdToken();
                    setUserToken(token);

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
                        setError("Failed to load user profile.");
                    }

                } else {
                    router.push("/");
                }
            });
            return () => unsubscribe();
        };
        initAuth();
    }, [router]);

    /**
     * Fetches dashboard data using an Async "Start -> Poll" pattern.
     * This avoids 60s timeouts on Firebase Hosting by breaking the operation into:
     * 1. Triggering the job.
     * 2. Polling for completion.
     */
    const fetchData = async () => {
        if (!studentId || !userToken) return;

        setLoading(true);
        setError(null);

        try {
            // Step 1: Start the refresh job
            // We tell the backend to start processing in the background.
            const startRes = await fetch("/api/aura", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${userToken}`,
                    "X-Authorization": `Bearer ${userToken}`
                },
                body: JSON.stringify({
                    role: "student",
                    action: "start_dashboard_refresh",
                    studentId,
                    auth_token: userToken,
                }),
            });

            if (!startRes.ok) throw new Error("Failed to start dashboard refresh");

            // Step 2: Poll for results
            // We check the status every 3 seconds until it's 'completed' or times out.
            const pollInterval = 3000; // 3 seconds
            const maxAttempts = 40; // 2 minutes timeout (40 * 3s = 120s)
            let attempts = 0;

            const poll = async () => {
                if (attempts >= maxAttempts) {
                    setError("Dashboard analysis timed out. Please try again later.");
                    setLoading(false);
                    return;
                }

                attempts++;

                try {
                    // Check status
                    const res = await fetch("/api/aura", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${userToken}`,
                            "X-Authorization": `Bearer ${userToken}`
                        },
                        body: JSON.stringify({
                            role: "student",
                            action: "get_dashboard",
                            studentId,
                            auth_token: userToken,
                        }),
                    });

                    if (!res.ok) throw new Error(`Server responded with ${res.status}`);

                    const json = await res.json();

                    // Handle different statuses
                    if (json.status === "processing") {
                        // Still working... wait and try again
                        setTimeout(poll, pollInterval);
                    } else if (json.status === "completed") {
                        // Success! Render the data.
                        setData(json);
                        setLoading(false);
                    } else if (json.status === "error") {
                        // Backend reported an error
                        setError(json.error || "An error occurred during analysis.");
                        setLoading(false);
                    } else if (json.status === "not_started") {
                        // Should not happen if we just started, but retry just in case
                        setTimeout(poll, pollInterval);
                    } else {
                        // Fallback for unexpected response
                        setError("Received invalid response from server.");
                        setLoading(false);
                    }
                } catch (e) {
                    console.error("Polling error:", e);
                    // Retry on network error (e.g. temporary glitch)
                    setTimeout(poll, pollInterval);
                }
            };

            // Kick off the polling loop
            poll();

        } catch (err) {
            console.error("Failed to fetch Aura data", err);
            setError("Failed to load dashboard. The server might be busy analyzing your schedule.");
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [studentId, userToken]);

    const [auraResponse, setAuraResponse] = useState<string | null>(null);
    const [lastQuery, setLastQuery] = useState<string | null>(null);

    const handleAuraMessage = async (message: string) => {
        setIsProcessing(true);
        setAuraResponse(null);
        setLastQuery(message);
        try {
            const res = await fetch("/api/aura", {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${userToken}`,
                    "X-Authorization": `Bearer ${userToken}`
                },
                body: JSON.stringify({
                    role: "student",
                    action: "chat",
                    studentId,
                    message,
                    auth_token: userToken,
                }),
            });

            const data = await res.json();
            if (data.response) {
                setAuraResponse(data.response);
            } else if (data.error) {
                setAuraResponse(`Error: ${data.error}`);
            }
        } catch (error) {
            console.error("Chat error:", error);
            setAuraResponse("Sorry, I couldn't reach Aura right now.");
        } finally {
            setIsProcessing(false);
        }
    };

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
        if (a.state === 'TURNED_IN' || a.state === 'RETURNED') return '#22c55e';
        if (!a.due || a.due === "No due date") return '#eab308';

        const due = new Date(a.due);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const dueEndOfDay = new Date(due);
        dueEndOfDay.setHours(23, 59, 59, 999);

        if (dueEndOfDay < today) return '#ef4444';

        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        tomorrow.setHours(23, 59, 59, 999);

        if (dueEndOfDay <= tomorrow) return '#f97316';
        return '#eab308';
    };

    const currentAssignments = data?.assignments?.filter((a: Assignment) => !isOld(a.due) && !hasNoDueDate(a)) || [];
    const noDueAssignments = data?.assignments?.filter((a: Assignment) => hasNoDueDate(a)) || [];
    const oldAssignments = data?.assignments?.filter((a: Assignment) => isOld(a.due)) || [];

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white p-6">
            <div className="max-w-7xl mx-auto">
                {/* Section 1: Header & Aura Input */}
                <div
                    className="mb-8 flex flex-col items-center"
                    style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '2rem', width: '100%' }}
                >
                    <h1 className="text-3xl font-bold text-white mb-2 text-center" style={{ textAlign: 'center', marginBottom: '0.5rem' }}>
                        Hello, {loading ? <span className="animate-pulse bg-white/10 rounded px-4 text-transparent">Loading Name</span> : (studentId.split('@')[0])}
                    </h1>
                    <p className="text-gray-400 mb-6 text-center" style={{ color: '#9ca3af', marginBottom: '1.5rem', textAlign: 'center' }}>What would you like to achieve today?</p>

                    <div
                        className="w-full max-w-2xl"
                        style={{ width: '100%', maxWidth: '42rem' }}
                    >
                        <AuraInput
                            onSend={handleAuraMessage}
                            isProcessing={isProcessing}
                        />
                    </div>

                    {error && (
                        <div className="mt-4 p-4 bg-red-900/30 border border-red-500/30 rounded-lg max-w-2xl mx-auto text-center animate-in fade-in slide-in-from-top-2">
                            <p className="text-red-200 mb-2">{error}</p>
                            <button
                                onClick={fetchData}
                                className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-200 rounded-lg transition-colors text-sm"
                            >
                                Retry Loading Dashboard
                            </button>
                        </div>
                    )}

                    {auraResponse && (
                        <div className="mt-4 p-4 bg-cyan-900/30 border border-cyan-500/30 rounded-lg max-w-2xl mx-auto text-left animate-in fade-in slide-in-from-top-2">
                            <div className="mb-3 pb-3 border-b border-white/10">
                                <div className="text-xs text-gray-400 font-bold mb-1">YOUR PROMPT</div>
                                <div className="text-white italic">"{lastQuery}"</div>
                            </div>
                            <div>
                                <div className="text-xs text-cyan-400 font-bold mb-1">AURA SAYS</div>
                                <div className="text-gray-200">{auraResponse}</div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Section 2: Main Grid (Today, Assignments, Calendar) */}
                <div
                    className="flex flex-row flex-nowrap gap-6 mb-8 overflow-x-auto pb-4 w-full"
                    style={{ display: 'flex', flexDirection: 'row', flexWrap: 'nowrap', overflowX: 'auto' }}
                >
                    {/* ... columns ... */}
                    {/* Column 1: Today's Plan */}
                    <DashboardColumn
                        title="Today's Plan"
                        icon={<Clock size={20} />}
                        className="flex-1 min-w-[300px]"
                        style={{ minWidth: '300px', flex: '1 1 0px' }}
                    >
                        {loading && (
                            <>
                                <SkeletonCard />
                                <SkeletonCard />
                                <SkeletonCard />
                            </>
                        )}
                        {!loading && data?.daily_plan?.length === 0 && (
                            <p className="text-gray-400 text-center py-4">No tasks planned for today.</p>
                        )}
                        {!loading && data?.daily_plan?.map((item: PlanItem) => (
                            <div
                                key={item.task_id}
                                className="mb-3 p-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                            >
                                <div className="flex justify-between items-start mb-1">
                                    <span className="font-mono text-sm text-cyan-300">{item.time}</span>
                                    <span
                                        className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-gray-300"
                                    >
                                        {item.difficulty_tag}
                                    </span>
                                </div>
                                <div
                                    className="font-medium mb-1"
                                    style={{ color: getAssignmentColor(item) }}
                                >
                                    {item.title}
                                </div>
                                <div className="text-xs text-gray-400">
                                    {item.subject} {item.due ? `• Due ${item.due}` : ""}
                                </div>
                            </div>
                        ))}
                    </DashboardColumn>

                    {/* Column 2: Current Assignments */}
                    <DashboardColumn
                        title="Current Assignments"
                        icon={<List size={20} />}
                        className="flex-1 min-w-[300px]"
                        style={{ minWidth: '300px', flex: '1 1 0px' }}
                    >
                        {loading && (
                            <>
                                <SkeletonCard />
                                <SkeletonCard />
                                <SkeletonCard />
                                <SkeletonCard />
                            </>
                        )}
                        {!loading && currentAssignments.map((a: Assignment) => (
                            <div
                                key={a.id}
                                className="mb-3 p-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors group"
                            >
                                <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                        <div
                                            className="font-medium mb-1 group-hover:text-cyan-300 transition-colors"
                                            style={{ color: getAssignmentColor(a) }}
                                        >
                                            {a.title}
                                        </div>
                                        <div className="text-xs text-gray-400">
                                            {a.subject}
                                        </div>
                                    </div>
                                    {a.due && (
                                        <span className="text-xs text-gray-500 font-mono whitespace-nowrap ml-2">
                                            {a.due}
                                        </span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </DashboardColumn>

                    {/* Column 3: Calendar */}
                    <DashboardColumn
                        title="Calendar"
                        icon={<Calendar size={20} />}
                        className="flex-1 min-w-[300px]"
                        style={{ minWidth: '300px', flex: '1 1 0px' }}
                    >
                        {loading && (
                            <>
                                <SkeletonCard />
                                <SkeletonCard />
                                <SkeletonCard />
                            </>
                        )}
                        {!loading && (!data?.calendar_events || data.calendar_events.length === 0) && (
                            <div className="flex flex-col items-center justify-center h-full text-gray-500 py-8">
                                <Calendar size={48} className="mb-4 opacity-20" />
                                <p>No events today</p>
                            </div>
                        )}
                        {!loading && data?.calendar_events?.map((event: any) => {
                            const start = event.start.dateTime ? new Date(event.start.dateTime) : new Date(event.start.date);
                            const end = event.end.dateTime ? new Date(event.end.dateTime) : new Date(event.end.date);
                            const timeStr = event.start.dateTime
                                ? `${start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - ${end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
                                : "All Day";

                            return (
                                <div key={event.id} className="mb-3 p-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
                                    <div className="text-xs text-cyan-300 font-mono mb-1">{timeStr}</div>
                                    <div className="font-medium text-white">{event.summary}</div>
                                </div>
                            );
                        })}
                    </DashboardColumn>
                </div>

                {/* Section 3: Bottom Grid (No Due Date, Past Due) */}
                <div
                    className="flex flex-row flex-nowrap gap-6 w-full"
                    style={{ display: 'flex', flexDirection: 'row', flexWrap: 'nowrap' }}
                >
                    <div className="flex-1 min-w-[300px]" style={{ flex: '1 1 0px', minWidth: '300px' }}>
                        <CollapsibleSection title="No Due Date" count={loading ? undefined : noDueAssignments.length}>
                            {loading ? (
                                <div className="animate-pulse space-y-2">
                                    <div className="h-10 bg-white/5 rounded"></div>
                                    <div className="h-10 bg-white/5 rounded"></div>
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 gap-3">
                                    {noDueAssignments.map((a: Assignment) => (
                                        <div key={a.id} className="p-3 rounded bg-white/5 border border-white/10">
                                            <div className="font-medium text-gray-300">{a.title}</div>
                                            <div className="text-xs text-gray-500">{a.subject}</div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </CollapsibleSection>
                    </div>

                    <div className="flex-1 min-w-[300px]" style={{ flex: '1 1 0px', minWidth: '300px' }}>
                        <CollapsibleSection title="Past Due" count={loading ? undefined : oldAssignments.length}>
                            {loading ? (
                                <div className="animate-pulse space-y-2">
                                    <div className="h-10 bg-white/5 rounded"></div>
                                    <div className="h-10 bg-white/5 rounded"></div>
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 gap-3">
                                    {oldAssignments.map((a: Assignment) => (
                                        <div key={a.id} className="p-3 rounded bg-white/5 border border-white/10 opacity-60">
                                            <div className="font-medium text-red-400">{a.title}</div>
                                            <div className="text-xs text-gray-500">{a.subject} • Due {a.due}</div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </CollapsibleSection>
                    </div>
                </div>

                {/* Hint Panel (Hidden or integrated differently?) */}
                {/* <div className="fixed bottom-4 right-4">
                    <HintPanel />
                </div> */}
            </div>
        </div>
    );
}
