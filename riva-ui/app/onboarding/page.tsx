"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
    User,
    Mail,
    Plus,
    Trash2,
    ArrowRight,
    CheckCircle2,
    School,
    Users,
    Loader2
} from "lucide-react";

export default function OnboardingPage() {
    const router = useRouter();
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        studentName: "",
        studentEmails: ["", ""],
        parentEmails: [""],
    });
    const [loading, setLoading] = useState(false);
    const [authStatus, setAuthStatus] = useState<Record<string, string>>({});

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleStudentEmailChange = (index: number, value: string) => {
        const newEmails = [...formData.studentEmails];
        newEmails[index] = value;
        setFormData({ ...formData, studentEmails: newEmails });
    };

    const addStudentEmailField = () => {
        setFormData({ ...formData, studentEmails: [...formData.studentEmails, ""] });
    };

    const removeStudentEmailField = (index: number) => {
        if (formData.studentEmails.length > 1) {
            const newEmails = formData.studentEmails.filter((_, i) => i !== index);
            setFormData({ ...formData, studentEmails: newEmails });
        }
    };

    const handleParentEmailChange = (index: number, value: string) => {
        const newEmails = [...formData.parentEmails];
        newEmails[index] = value;
        setFormData({ ...formData, parentEmails: newEmails });
    };

    const addParentEmailField = () => {
        setFormData({ ...formData, parentEmails: [...formData.parentEmails, ""] });
    };

    const removeParentEmailField = (index: number) => {
        if (formData.parentEmails.length > 1) {
            const newEmails = formData.parentEmails.filter((_, i) => i !== index);
            setFormData({ ...formData, parentEmails: newEmails });
        }
    };

    const handleSubmitDetails = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const validStudentEmails = formData.studentEmails.filter(email => email.trim() !== "");
            const validParentEmails = formData.parentEmails.filter(email => email.trim() !== "");

            if (validStudentEmails.length === 0) {
                alert("Please enter at least one student email.");
                setLoading(false);
                return;
            }

            if (validParentEmails.length === 0) {
                alert("Please enter at least one parent email.");
                setLoading(false);
                return;
            }

            const res = await fetch("/api/onboarding", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    student_name: formData.studentName,
                    student_emails: validStudentEmails,
                    parent_emails: validParentEmails,
                }),
            });

            const json = await res.json();

            if (res.ok) {
                setStep(2);
            } else {
                console.error("Submission failed:", json);
                alert(`Failed to save details: ${json.message || "Unknown error"}`);
            }
        } catch (err) {
            console.error("Error submitting form:", err);
            alert("An error occurred while saving details.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const handleMessage = (event: MessageEvent) => {
            if (event.origin !== window.location.origin) return;
            if (event.data?.type === "AUTH_SUCCESS" && event.data?.email) {
                setAuthStatus(prev => ({ ...prev, [event.data.email]: "connected" }));
            }
        };

        window.addEventListener("message", handleMessage);
        return () => window.removeEventListener("message", handleMessage);
    }, []);

    const handleConnectGoogle = async (email: string) => {
        setLoading(true);
        // Open window immediately to avoid popup blockers
        const authWindow = window.open("", "_blank", "width=600,height=700");

        try {
            const redirectUri = window.location.origin + "/auth/callback";
            const res = await fetch("/api/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: email,
                    redirect_uri: redirectUri,
                    login_hint: email,
                }),
            });
            const json = await res.json();
            if (json.url && authWindow) {
                authWindow.location.href = json.url;
            } else {
                authWindow?.close();
                alert("Failed to get auth URL");
            }
        } catch (err) {
            console.error(err);
            authWindow?.close();
            alert("An error occurred.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-900 via-purple-900 to-slate-900 overflow-y-auto">
            <div className="min-h-full w-full flex items-center justify-center p-4 font-sans relative">
                <div className="absolute inset-0 overflow-hidden pointer-events-none">
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
                </div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-white/10 backdrop-blur-xl rounded-3xl p-12 w-full max-w-2xl shadow-2xl border border-white/10 relative z-10"
                >
                    <div className="text-center mb-10">
                        <motion.div
                            initial={{ scale: 0.9 }}
                            animate={{ scale: 1 }}
                            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-pink-500 to-violet-600 mb-4 shadow-lg shadow-purple-500/30"
                        >
                            <School className="w-8 h-8 text-white" />
                        </motion.div>
                        <h1 className="text-4xl font-bold text-white mb-2 tracking-tight">Welcome to Riva AI</h1>
                        <p className="text-indigo-200 text-lg">Your personal academic success companion</p>
                    </div>

                    <AnimatePresence mode="wait">
                        {step === 1 && (
                            <motion.form
                                key="step1"
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 20 }}
                                onSubmit={handleSubmitDetails}
                                className="space-y-10"
                            >
                                <div className="space-y-8">
                                    {/* Student Name */}
                                    <div className="space-y-2">
                                        <label className="flex items-center gap-2 text-sm font-medium text-indigo-200">
                                            <User className="w-4 h-4" /> Student Name
                                        </label>
                                        <input
                                            type="text"
                                            name="studentName"
                                            value={formData.studentName}
                                            onChange={handleChange}
                                            className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all"
                                            placeholder="e.g. Alex Smith"
                                            required
                                        />
                                    </div>

                                    {/* Student Emails */}
                                    <div className="space-y-3">
                                        <label className="flex items-center gap-2 text-sm font-medium text-indigo-200">
                                            <Mail className="w-4 h-4" /> Student Emails
                                        </label>
                                        <div className="space-y-3">
                                            {formData.studentEmails.map((email, index) => (
                                                <motion.div
                                                    key={`student-${index}`}
                                                    initial={{ opacity: 0, height: 0 }}
                                                    animate={{ opacity: 1, height: "auto" }}
                                                    className="flex gap-2"
                                                >
                                                    <input
                                                        type="email"
                                                        value={email}
                                                        onChange={(e) => handleStudentEmailChange(index, e.target.value)}
                                                        className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all"
                                                        placeholder={index === 0 ? "Primary Email (Gmail)" : "Additional Email (e.g. Sports, Clubs)"}
                                                        required={index === 0}
                                                    />
                                                    {formData.studentEmails.length > 1 && (
                                                        <button
                                                            type="button"
                                                            onClick={() => removeStudentEmailField(index)}
                                                            className="p-3 rounded-xl bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20 transition-colors"
                                                        >
                                                            <Trash2 className="w-5 h-5" />
                                                        </button>
                                                    )}
                                                </motion.div>
                                            ))}
                                        </div>
                                        <button
                                            type="button"
                                            onClick={addStudentEmailField}
                                            className="text-sm text-pink-400 hover:text-pink-300 flex items-center gap-1 font-medium transition-colors"
                                        >
                                            <Plus className="w-4 h-4" /> Add another student email
                                        </button>
                                    </div>

                                    {/* Parent Emails */}
                                    <div className="space-y-3">
                                        <label className="flex items-center gap-2 text-sm font-medium text-indigo-200">
                                            <Users className="w-4 h-4" /> Parent Emails
                                        </label>
                                        <div className="space-y-3">
                                            {formData.parentEmails.map((email, index) => (
                                                <motion.div
                                                    key={`parent-${index}`}
                                                    initial={{ opacity: 0, height: 0 }}
                                                    animate={{ opacity: 1, height: "auto" }}
                                                    className="flex gap-2"
                                                >
                                                    <input
                                                        type="email"
                                                        value={email}
                                                        onChange={(e) => handleParentEmailChange(index, e.target.value)}
                                                        className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all"
                                                        placeholder="parent@example.com"
                                                        required={index === 0}
                                                    />
                                                    {formData.parentEmails.length > 1 && (
                                                        <button
                                                            type="button"
                                                            onClick={() => removeParentEmailField(index)}
                                                            className="p-3 rounded-xl bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20 transition-colors"
                                                        >
                                                            <Trash2 className="w-5 h-5" />
                                                        </button>
                                                    )}
                                                </motion.div>
                                            ))}
                                        </div>
                                        <button
                                            type="button"
                                            onClick={addParentEmailField}
                                            className="text-sm text-pink-400 hover:text-pink-300 flex items-center gap-1 font-medium transition-colors"
                                        >
                                            <Plus className="w-4 h-4" /> Add another parent email
                                        </button>
                                    </div>
                                </div>

                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full py-4 rounded-xl bg-gradient-to-r from-pink-500 to-violet-600 text-white font-bold text-lg shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 transform hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                                >
                                    {loading ? (
                                        <Loader2 className="w-6 h-6 animate-spin" />
                                    ) : (
                                        <>
                                            Continue <ArrowRight className="w-5 h-5" />
                                        </>
                                    )}
                                </button>
                            </motion.form>
                        )}

                        {step === 2 && (
                            <motion.div
                                key="step2"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="space-y-8"
                            >
                                <div className="p-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-4">
                                    <div className="p-3 rounded-full bg-emerald-500/20 text-emerald-400">
                                        <CheckCircle2 className="w-6 h-6" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-semibold text-emerald-200">Profile Created!</h3>
                                        <p className="text-emerald-200/60">Your details have been saved successfully.</p>
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <h3 className="text-xl font-semibold text-white">Connect Your Accounts</h3>
                                    <p className="text-indigo-200">
                                        Please authenticate each student email to sync assignments from Google Classroom.
                                    </p>

                                    <div className="space-y-4 mt-4">
                                        {formData.studentEmails.filter(e => e.trim()).map((email, index) => (
                                            <div
                                                key={index}
                                                className="p-4 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between group hover:bg-white/10 transition-colors"
                                            >
                                                <div className="flex items-center gap-3">
                                                    <div className="w-10 h-10 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-300">
                                                        <Mail className="w-5 h-5" />
                                                    </div>
                                                    <div>
                                                        <p className="text-white font-medium">{email}</p>
                                                        <p className="text-xs text-indigo-300">Google Classroom</p>
                                                    </div>
                                                </div>
                                                {authStatus[email] === "connected" ? (
                                                    <button
                                                        disabled
                                                        className="px-4 py-2 rounded-lg bg-emerald-500/20 text-emerald-400 font-semibold text-sm border border-emerald-500/20 flex items-center gap-2 cursor-default"
                                                    >
                                                        <CheckCircle2 className="w-4 h-4" />
                                                        Connected
                                                    </button>
                                                ) : (
                                                    <button
                                                        onClick={() => handleConnectGoogle(email)}
                                                        disabled={loading}
                                                        className="px-4 py-2 rounded-lg bg-white text-gray-900 font-semibold text-sm shadow hover:bg-gray-100 transition-all flex items-center gap-2"
                                                    >
                                                        <div className="w-5 h-5 bg-white rounded-full flex items-center justify-center">
                                                            <img src="https://www.google.com/favicon.ico" alt="G" className="w-4 h-4" />
                                                        </div>
                                                        Connect to Classroom
                                                    </button>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>
            </div>
        </div>
    );
}
