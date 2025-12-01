import { NextResponse } from "next/server";

export async function GET(request: Request) {
    try {
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://backend:8000";
        const authHeader = request.headers.get("authorization");

        const headers: HeadersInit = {
            "Content-Type": "application/json",
        };

        if (authHeader) {
            headers["Authorization"] = authHeader;
        }

        const res = await fetch(`${backendUrl}/api/user`, {
            method: "GET",
            headers: headers,
        });

        if (!res.ok) {
            const errorText = await res.text();
            console.error("Backend user fetch error:", res.status, errorText);
            return NextResponse.json({ error: "Backend fetch failed", details: errorText }, { status: res.status });
        }

        const data = await res.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Proxy user fetch error:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
