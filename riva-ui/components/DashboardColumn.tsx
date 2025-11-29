import React from 'react';

interface DashboardColumnProps {
    title: string;
    children: React.ReactNode;
    className?: string;
    icon?: React.ReactNode;
    style?: React.CSSProperties;
}

const DashboardColumn: React.FC<DashboardColumnProps> = ({ title, children, className = '', icon, style }) => {
    return (
        <div
            className={`flex flex-col h-full bg-black/20 backdrop-blur-sm rounded-xl border border-white/10 overflow-hidden ${className}`}
            style={style}
        >
            <div className="p-4 border-b border-white/10 bg-white/5 flex items-center gap-2">
                {icon && <span className="text-cyan-400">{icon}</span>}
                <h2 className="text-lg font-semibold text-white tracking-wide">{title}</h2>
            </div>
            <div className="flex-1 overflow-y-auto p-4 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                {children}
            </div>
        </div>
    );
};

export default DashboardColumn;
