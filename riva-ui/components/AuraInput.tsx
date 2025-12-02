import React, { useState } from 'react';
import { Send } from 'lucide-react';

interface AuraInputProps {
    onSend: (message: string) => void;
    isProcessing?: boolean;
}

const SUGGESTIONS = [
    "What homework do I have?",
    "Create my study plan for tomorrow",
    "Schedule my homework into my calendar"
];

const AuraInput: React.FC<AuraInputProps> = ({ onSend, isProcessing }) => {
    /**
     * AuraInput Component
     * 
     * A chat-like input field for interacting with the Aura agent.
     * Includes:
     * - Text input with send button
     * - Quick suggestion chips for common queries
     * - Loading state handling
     */
    const [input, setInput] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (input.trim() && !isProcessing) {
            onSend(input.trim());
            setInput('');
        }
    };

    return (
        <div className="w-full max-w-3xl mx-auto mb-8">
            <form onSubmit={handleSubmit} className="relative mb-4">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask Aura..."
                    className="w-full p-4 pr-12 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-cyan-400 shadow-lg text-lg transition-all"
                    disabled={isProcessing}
                />
                <button
                    type="submit"
                    disabled={!input.trim() || isProcessing}
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-full bg-cyan-500 hover:bg-cyan-400 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    <Send size={20} />
                </button>
            </form>

            <div className="flex flex-wrap justify-center gap-2">
                {SUGGESTIONS.map((suggestion) => (
                    <button
                        key={suggestion}
                        onClick={() => onSend(suggestion)}
                        disabled={isProcessing}
                        className="px-4 py-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-sm text-cyan-200 transition-colors"
                    >
                        {suggestion}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default AuraInput;
