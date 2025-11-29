"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Loader2, CheckCircle2, XCircle } from "lucide-react";

function CallbackContent() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
    const [message, setMessage] = useState("Authenticating...");

    useEffect(() => {
        const code = searchParams.get("code");
        const error = searchParams.get("error");
        const state = searchParams.get("state"); // This is the email

        if (error) {
            setStatus("error");
            setMessage(`Authentication failed: ${error}`);
            return;
        }

        if (!code) {
            setStatus("error");
            setMessage("No authentication code received.");
            return;
        }

        if (!state) {
            setStatus("error");
            setMessage("No state (email) received.");
            return;
        }

        const exchangeCode = async () => {
            try {
                const email = state; // We passed email as state
                const redirectUri = window.location.origin + "/auth/callback";

                const res = await fetch("/api/auth/callback", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        email: email,
                        code: code,
                        redirect_uri: redirectUri,
                    }),
                });

                const json = await res.json();

                if (res.ok && json.status === "success") {
                    setStatus("success");
                    setMessage(`Successfully connected ${email}! You can close this tab.`);

                    // Notify opener
                    if (window.opener) {
                        window.opener.postMessage({ type: "AUTH_SUCCESS", email: email }, window.location.origin);
                    }

                    setTimeout(() => {
                        window.close();
                        // Fallback if close is blocked
                        router.push("/onboarding?step=2");
                    }, 1500);
                } else {
                    throw new Error(json.error || "Failed to exchange token.");
                }
            } catch (err: any) {
                console.error(err);
                setStatus("error");
                setMessage(err.message || "An error occurred.");
            }
        };

        exchangeCode();
    }, [searchParams, router]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white p-4">
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-8 max-w-md w-full text-center border border-white/10 shadow-2xl">
                {status === "loading" && (
                    <div className="flex flex-col items-center gap-4">
                        <Loader2 className="w-12 h-12 text-indigo-400 animate-spin" />
                        <h2 className="text-xl font-semibold">Connecting to Google Classroom...</h2>
                        <p className="text-indigo-200 text-sm">Please wait while we secure your connection.</p>
                    </div>
                )}
                {status === "success" && (
                    <div className="flex flex-col items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                            <CheckCircle2 className="w-8 h-8" />
                        </div>
                        <h2 className="text-xl font-semibold text-emerald-400">Connected!</h2>
                        <p className="text-indigo-200 text-sm">{message}</p>
                    </div>
                )}
                {status === "error" && (
                    <div className="flex flex-col items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center text-red-400">
                            <XCircle className="w-8 h-8" />
                        </div>
                        <h2 className="text-xl font-semibold text-red-400">Connection Failed</h2>
                        <p className="text-red-200/80 text-sm">{message}</p>
                        <button
                            onClick={() => router.push("/onboarding?step=2")}
                            className="mt-4 px-6 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors text-sm font-medium"
                        >
                            Return to Onboarding
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default function AuthCallbackPage() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <CallbackContent />
        </Suspense>
    );
}
