// app/parent/page.tsx
import ParentDashboard from "@/components/ParentDashboard";

export default function ParentPage() {
    return (
        <div style={{ maxWidth: 900, margin: "0 auto" }}>
            <h1 style={{ fontSize: "1.5rem", marginBottom: "1rem" }}>
                Riva.ai – Parent View
            </h1>
            <ParentDashboard />
        </div>
    );
}
