import React from 'react';
import type { RiskLevel } from '../../types';

interface RiskBadgeProps {
  level: RiskLevel;
  score?: number;
  className?: string;
  showDot?: boolean;
}

const BADGE_STYLES: Record<RiskLevel, { bg: string; text: string; border: string; dot: string }> = {
  LOW: {
    bg: 'bg-emerald-50/90',
    text: 'text-emerald-700',
    border: 'border-emerald-200/80',
    dot: 'bg-emerald-500',
  },
  MEDIUM: {
    bg: 'bg-amber-50/90',
    text: 'text-amber-800',
    border: 'border-amber-200/80',
    dot: 'bg-amber-500',
  },
  HIGH: {
    bg: 'bg-orange-50/90',
    text: 'text-orange-800',
    border: 'border-orange-200/80',
    dot: 'bg-orange-500',
  },
  CRITICAL: {
    bg: 'bg-red-50/90',
    text: 'text-red-700',
    border: 'border-red-200/80',
    dot: 'bg-red-500 animate-pulse',
  },
};

export default function RiskBadge({ level, score, className = '', showDot = true }: RiskBadgeProps) {
  const style = BADGE_STYLES[level] || BADGE_STYLES.LOW;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border tracking-wide transition-colors ${style.bg} ${style.text} ${style.border} ${className}`}
    >
      {showDot && <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />}
      <span>{level}</span>
      {score !== undefined && (
        <span className="font-mono text-[11px] font-bold opacity-85">
          ({score.toFixed(1)})
        </span>
      )}
    </span>
  );
}
