import React from "react";

export default function KPIChip({ percentage, withFiles, total, isLoading }) {
    if (isLoading) {
        return (
            <div className="h-8 w-40 rounded-full bg-gray-200/70 dark:bg-gray-700/50 animate-pulse" />
        );
    }

    return (
        <div className="flex items-center gap-2 px-3 h-8 rounded-full border bg-white/60 dark:bg-white/5 dark:border-white/10 shadow-sm">
            <span className="text-sm font-medium">
                {Number(percentage ?? 0).toFixed(2)}%
            </span>
            <span className="text-[11px] opacity-70">
                {withFiles ?? 0}/{total ?? 0} con archivos
            </span>
            <div className="w-24 h-1.5 rounded-full bg-gray-200 dark:bg-white/10 overflow-hidden">
                <div
                    className="h-1.5 rounded-full bg-primary"
                    style={{ width: `${Math.min(100, Math.max(0, percentage || 0))}%` }}
                />
            </div>
        </div>
    );
}
