// components/StudentDashboard.tsx
"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type Message = {
    id: number;
    from: "student" | "aura";
    text: string;
    time: string;
};

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

export default function StudentDashboard() {
    const router = useRouter();
    const [studentId, setStudentId] = useState<string>("");
    const [studentName, setStudentName] = useState<string>("");
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<any>(null);
    const [userToken, setUserToken] = useState<string>("");
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const [messages, setMessages] = useState<Message[]>([
        {
            id: 1,
            from: "student",
            text: "Hey Aura! Can you help me plan my homework so I don't feel rushed?",
            time: new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }),
        },
        {
            id: 2,
            from: "aura",
            text: "Of course! I can help you organize your assignments and create a balanced schedule.",
            time: new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }),
        },
    ]);

    const [input, setInput] = useState("");

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
                            const email = json.user.student_emails[0];
                            setStudentId(email);
                            setStudentName(email.split("@")[0]);
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

    const fetchData = async () => {
        if (!studentId || !userToken) return;

        setLoading(true);
        setError(null);
        try {
            const res = await fetch("/api/aura", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${userToken}`,
                    "X-Authorization": `Bearer ${userToken}`,
                },
                body: JSON.stringify({
                    role: "student",
                    action: "get_dashboard",
                    studentId,
                    auth_token: userToken,
                }),
            });

            if (!res.ok) {
                throw new Error(`Server responded with ${res.status}`);
            }

            const json = await res.json();
            if (json.error) {
                console.error(json.error);
                if (json.error.includes("Access denied") || json.error.includes("Invalid token")) {
                    router.push("/");
                } else {
                    setError(json.error);
                }
            } else {
                setData(json);
            }
        } catch (err) {
            console.error("Failed to fetch Aura data", err);
            setError("Failed to load dashboard. The server might be busy analyzing your schedule.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [studentId, userToken]);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isProcessing) return;

        const timestamp = new Date().toLocaleTimeString([], {
            hour: "numeric",
            minute: "2-digit",
        });

        const studentMessage: Message = {
            id: Date.now(),
            from: "student",
            text: input.trim(),
            time: timestamp,
        };

        setMessages((prev) => [...prev, studentMessage]);
        setInput("");
        setIsProcessing(true);

        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/aura`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${userToken}`,
                    "X-Authorization": `Bearer ${userToken}`,
                },
                body: JSON.stringify({
                    role: "student",
                    action: "chat",
                    studentId,
                    message: input.trim(),
                    auth_token: userToken,
                }),
            });

            const responseData = await res.json();
            const auraMessage: Message = {
                id: Date.now() + 1,
                from: "aura",
                text: responseData.response || "I'm here to help! What would you like to know?",
                time: timestamp,
            };
            setMessages((prev) => [...prev, auraMessage]);
        } catch (error) {
            console.error("Chat error:", error);
            const errorMessage: Message = {
                id: Date.now() + 1,
                from: "aura",
                text: "Sorry, I couldn't process that right now. Please try again.",
                time: timestamp,
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsProcessing(false);
        }
    };

    const getAssignmentColor = (a: Assignment | PlanItem) => {
        if (a.state === "TURNED_IN" || a.state === "RETURNED") return "#22c55e";
        if (!a.due || a.due === "No due date") return "#eab308";

        const due = new Date(a.due);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const dueEndOfDay = new Date(due);
        dueEndOfDay.setHours(23, 59, 59, 999);

        if (dueEndOfDay < today) return "#ef4444";

        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        tomorrow.setHours(23, 59, 59, 999);

        if (dueEndOfDay <= tomorrow) return "#f97316";
        return "#eab308";
    };

    const todaysPlan = data?.daily_plan?.slice(0, 3) || [];
    const todaysAssignments = data?.assignments?.filter((a: Assignment) => {
        if (!a.due || a.due === "No due date") return false;
        const due = new Date(a.due);
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        return due <= tomorrow;
    }).slice(0, 3) || [];

    const upcomingEvents = data?.calendar_events?.slice(0, 2) || [];

    return (
        <div className="min-h-screen w-full bg-gradient-to-br from-[#0E0F23] via-[#14162E] to-[#1A1C3A] text-slate-100 flex flex-col">

            {/* Top Bar */}
            <header className="flex items-center justify-between px-6 py-4 border-b border-white/10 backdrop-blur-md">
                <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-2xl bg-gradient-to-tr from-pink-500 via-orange-400 to-yellow-300 flex items-center justify-center text-xl font-bold">
                        ⚡
                    </div>
                    <div>
                        <p className="text-sm font-semibold">Riva.ai — Aura for Students</p>
                        <p className="text-xs text-slate-400">Personalized study & schedule buddy</p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <div className="h-9 w-9 rounded-full bg-gradient-to-br from-orange-400 to-pink-500 text-white flex items-center justify-center font-bold">
                        {loading ? "..." : studentName.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <p className="text-sm font-semibold">
                            {loading ? "Loading..." : studentName}
                        </p>
                        <p className="text-xs text-slate-400">ELA · Math · XC</p>
                    </div>
                </div>
            </header>

            {/* Main Layout */}
            <main className="flex-1 px-6 py-6 grid grid-cols-1 lg:grid-cols-[260px_minmax(0,1.5fr)_260px] gap-6">

                {/* LEFT — Persona */}
                <aside className="bg-white/5 border border-white/10 rounded-2xl p-5 shadow-xl flex flex-col gap-5">
                    <h2 className="text-xs uppercase tracking-widest text-slate-400">Persona</h2>

                    <div className="flex items-center gap-4">
                        <div className="h-14 w-14 rounded-full bg-gradient-to-br from-pink-500 to-orange-400 flex items-center justify-center text-lg font-bold">
                            {loading ? "..." : studentName.charAt(0).toUpperCase()}
                        </div>
                        <div>
                            <p className="text-sm font-semibold">{loading ? "Loading..." : studentName}</p>
                            <p className="text-xs text-slate-400">Student • Runner • Curious Learner</p>
                        </div>
                    </div>

                    <div>
                        <p className="text-xs font-semibold text-slate-300 mb-2">✨ Goals Today</p>
                        {loading ? (
                            <div className="animate-pulse space-y-1">
                                <div className="h-3 bg-white/10 rounded w-full"></div>
                                <div className="h-3 bg-white/10 rounded w-3/4"></div>
                            </div>
                        ) : todaysPlan.length > 0 ? (
                            <ul className="text-xs text-slate-200 space-y-1">
                                {todaysPlan.map((item: PlanItem) => (
                                    <li key={item.task_id}>• {item.title}</li>
                                ))}
                            </ul>
                        ) : (
                            <p className="text-xs text-slate-400">No tasks planned yet</p>
                        )}
                    </div>

                    <div className="border-t border-white/10 pt-3">
                        <p className="text-xs font-semibold text-slate-300 mb-2">✨ How Aura Should Help</p>

                        <label className="text-xs flex gap-2 items-center">
                            <input type="checkbox" defaultChecked className="accent-purple-500" />
                            Keep me motivated
                        </label>

                        <label className="text-xs flex gap-2 items-center">
                            <input type="checkbox" defaultChecked className="accent-purple-500" />
                            Explain step-by-step
                        </label>

                        <label className="text-xs flex gap-2 items-center">
                            <input type="checkbox" className="accent-purple-500" />
                            Quiz me after homework
                        </label>
                    </div>

                    <div>
                        <p className="text-xs font-semibold text-slate-300 mb-2">🎨 Vibe</p>
                        <div className="flex flex-wrap gap-2">
                            <span className="px-2 py-1 text-[10px] rounded-full bg-white/10">Short explanations</span>
                            <span className="px-2 py-1 text-[10px] rounded-full bg-white/10">Friendly</span>
                            <span className="px-2 py-1 text-[10px] rounded-full bg-white/10">No yelling 😄</span>
                        </div>
                    </div>
                </aside>

                {/* CENTER — Chat */}
                <section className="bg-white/5 border border-white/10 rounded-2xl p-5 shadow-xl flex flex-col">
                    {/* Aura Header */}
                    <div className="flex items-center gap-3 mb-4">
                        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 via-cyan-400 to-emerald-400 flex items-center justify-center text-base font-bold">
                            A
                        </div>
                        <div>
                            <p className="text-sm font-semibold">Aura</p>
                            <p className="text-xs text-slate-400">
                                <span className="inline-block h-2 w-2 bg-green-400 rounded-full animate-pulse mr-1"></span>
                                Online — Personalized for {studentName || "you"}
                            </p>
                        </div>
                    </div>

                    {/* Error Display */}
                    {error && (
                        <div className="mb-4 p-3 bg-red-900/30 border border-red-500/30 rounded-lg">
                            <p className="text-red-200 text-sm mb-2">{error}</p>
                            <button
                                onClick={fetchData}
                                className="px-3 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-200 rounded text-xs transition-colors"
                            >
                                Retry
                            </button>
                        </div>
                    )}

                    {/* Chat Window */}
                    <div className="flex-1 overflow-y-auto space-y-4 bg-black/20 rounded-xl p-4 border border-white/10 min-h-[400px]">
                        {messages.map((m) => (
                            <div
                                key={m.id}
                                className={`flex gap-3 ${m.from === "student" ? "justify-end" : "justify-start"}`}
                            >
                                {m.from === "aura" && (
                                    <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-emerald-400 flex items-center justify-center text-[11px] font-bold flex-shrink-0">
                                        A
                                    </div>
                                )}

                                <div
                                    className={`max-w-[75%] p-3 text-xs rounded-2xl ${m.from === "student"
                                        ? "bg-gradient-to-tr from-orange-400 to-pink-500 text-white rounded-br-sm"
                                        : "bg-white/10 text-slate-200 rounded-bl-sm"
                                        }`}
                                >
                                    <p className="font-semibold text-[10px] opacity-70 mb-1">
                                        {m.from === "student" ? studentName || "You" : "Aura"}
                                    </p>
                                    <p className="whitespace-pre-wrap leading-snug">{m.text}</p>
                                    <p className="text-[10px] opacity-60 mt-1 text-right">{m.time}</p>
                                </div>

                                {m.from === "student" && (
                                    <div className="h-8 w-8 rounded-full bg-gradient-to-br from-orange-400 to-pink-500 flex items-center justify-center text-[11px] font-bold flex-shrink-0">
                                        {studentName.charAt(0).toUpperCase() || "S"}
                                    </div>
                                )}
                            </div>
                        ))}
                        {isProcessing && (
                            <div className="flex gap-3 justify-start">
                                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-emerald-400 flex items-center justify-center text-[11px] font-bold">
                                    A
                                </div>
                                <div className="bg-white/10 text-slate-200 rounded-2xl rounded-bl-sm p-3">
                                    <div className="flex gap-1">
                                        <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                                        <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                                        <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Input */}
                    <form onSubmit={handleSend} className="mt-4 flex gap-3 items-center">
                        <input
                            className="flex-1 bg-black/40 border border-white/10 rounded-full px-6 py-4 text-sm placeholder:text-slate-400 focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400/50 transition-all shadow-inner"
                            placeholder="Ask Aura…"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            disabled={isProcessing}
                        />
                        <button
                            type="submit"
                            disabled={isProcessing || !input.trim()}
                            className="h-14 w-14 rounded-full bg-gradient-to-br from-blue-500 via-cyan-400 to-emerald-400 flex items-center justify-center text-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-105 active:scale-95 shadow-lg shadow-purple-500/20"
                        >
                            ➤
                        </button>
                    </form>
                </section>

                {/* RIGHT — Context */}
                <aside className="hidden lg:flex flex-col bg-white/5 border border-white/10 rounded-2xl p-5 shadow-xl gap-5">
                    <h2 className="text-xs uppercase tracking-widest text-slate-400">Context</h2>

                    <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                        <p className="text-xs font-semibold mb-2">📚 Today&apos;s Homework</p>
                        {loading ? (
                            <div className="animate-pulse space-y-1">
                                <div className="h-3 bg-white/10 rounded w-full"></div>
                                <div className="h-3 bg-white/10 rounded w-3/4"></div>
                            </div>
                        ) : todaysAssignments.length > 0 ? (
                            <ul className="text-xs text-slate-200 space-y-1">
                                {todaysAssignments.map((a: Assignment) => (
                                    <li key={a.id} style={{ color: getAssignmentColor(a) }}>
                                        {a.subject}: {a.title}
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p className="text-xs text-slate-400">No homework due today</p>
                        )}
                    </div>

                    <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                        <p className="text-xs font-semibold mb-2">🏃 Schedule</p>
                        {loading ? (
                            <div className="animate-pulse space-y-1">
                                <div className="h-3 bg-white/10 rounded w-full"></div>
                                <div className="h-3 bg-white/10 rounded w-2/3"></div>
                            </div>
                        ) : upcomingEvents.length > 0 ? (
                            <ul className="text-xs text-slate-200 space-y-1">
                                {upcomingEvents.map((event: any) => {
                                    const start = event.start.dateTime ? new Date(event.start.dateTime) : new Date(event.start.date);
                                    const timeStr = event.start.dateTime
                                        ? start.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                                        : "All Day";
                                    return (
                                        <li key={event.id}>
                                            {event.summary} — {timeStr}
                                        </li>
                                    );
                                })}
                            </ul>
                        ) : (
                            <p className="text-xs text-slate-400">No events scheduled</p>
                        )}
                    </div>

                    <div className="bg-purple-500/20 border border-purple-400/30 rounded-xl p-4">
                        <p className="text-xs font-semibold text-purple-100 mb-2">💡 Aura Suggestion</p>
                        <p className="text-[11px] text-slate-200 leading-relaxed">
                            {loading
                                ? "Loading personalized suggestions..."
                                : data?.insights
                                    ? data.insights
                                    : "Connect Google Classroom + Calendar, and I can auto-plan your day."}
                        </p>
                    </div>
                </aside>

            </main>
        </div>
    );
}
