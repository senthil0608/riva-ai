// app/api/aura/route.ts
import { NextResponse } from "next/server";

const AURA_BACKEND_URL =
    process.env.AURA_BACKEND_URL || "http://localhost:8000/aura";

export async function POST(req: Request) {
    try {
        const body = await req.json();

        // Forward to your Python/ADK Aura endpoint
        const res = await fetch(AURA_BACKEND_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });

        if (!res.ok) {
            const text = await res.text();
            console.error("Aura backend error:", text);
            return NextResponse.json(
                { error: "Aura backend failed", details: text },
                { status: 500 }
            );
        }

        const data = await res.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Aura route error:", error);
        return NextResponse.json(
            { error: "Internal Server Error", details: String(error) },
            { status: 500 }
        );
    }
}
