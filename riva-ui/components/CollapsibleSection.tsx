import React, { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';

interface CollapsibleSectionProps {
    title: string;
    children: React.ReactNode;
    defaultExpanded?: boolean;
    count?: number;
}

const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({ title, children, defaultExpanded = false, count }) => {
    const [isExpanded, setIsExpanded] = useState(defaultExpanded);

    return (
        <div className="border border-white/10 rounded-lg bg-black/20 overflow-hidden mb-4">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center justify-between p-4 bg-white/5 hover:bg-white/10 transition-colors text-left"
            >
                <div className="flex items-center gap-2">
                    {isExpanded ? <ChevronDown size={20} className="text-cyan-400" /> : <ChevronRight size={20} className="text-cyan-400" />}
                    <span className="font-medium text-white">{title}</span>
                    {count !== undefined && (
                        <span className="px-2 py-0.5 rounded-full bg-white/10 text-xs text-gray-300">
                            {count}
                        </span>
                    )}
                </div>
            </button>

            {isExpanded && (
                <div className="p-4 border-t border-white/10">
                    {children}
                </div>
            )}
        </div>
    );
};

export default CollapsibleSection;
