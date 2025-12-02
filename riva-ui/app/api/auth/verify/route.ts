import { NextResponse } from "next/server";

export async function POST(request: Request) {
    /**
     * Verify Token Proxy
     * 
     * Proxies the token verification request from the frontend to the Python backend.
     * This is necessary to keep the backend URL hidden/internal and avoid CORS issues
     * if the backend is on a different domain (though currently they share a domain via rewrites).
     */
    try {
        const body = await request.json();
        const authHeader = request.headers.get("authorization");

        if (!authHeader) {
            return NextResponse.json({ error: "Missing Authorization header" }, { status: 401 });
        }

        const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://backend:8000";
        const res = await fetch(`${backendUrl}/api/auth/verify`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": authHeader,
            },
            body: JSON.stringify(body),
        });

        if (!res.ok) {
            const errorText = await res.text();
            console.error("Backend verify error:", res.status, errorText);
            return NextResponse.json({ error: "Backend verification failed", details: errorText }, { status: res.status });
        }

        const data = await res.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Proxy verify error:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
