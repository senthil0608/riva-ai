// app/student/page.tsx
import StudentDashboard from "@/components/StudentDashboard";

export default function StudentPage() {
    return (
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
            <h1 style={{ fontSize: "1.5rem", marginBottom: "1rem" }}>
                Riva.ai – Student View
            </h1>
            <StudentDashboard />
        </div>
    );
}
