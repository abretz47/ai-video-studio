"use client";

/**
 * Style configuration for each hook type
 */
const HOOK_STYLES: Record<
  string,
  { bg: string; text: string; label: string; code: string }
> = {
  hook: {
    bg: "bg-gray-100 dark:bg-gray-800",
    text: "text-gray-700 dark:text-gray-300",
    label: "Hook",
    code: "H",
  },
  reversal: {
    bg: "bg-gray-100 dark:bg-gray-800",
    text: "text-gray-700 dark:text-gray-300",
    label: "Reversal",
    code: "R",
  },
  payoff: {
    bg: "bg-gray-100 dark:bg-gray-800",
    text: "text-gray-700 dark:text-gray-300",
    label: "Payoff",
    code: "P",
  },
  cliffhanger: {
    bg: "bg-gray-100 dark:bg-gray-800",
    text: "text-gray-700 dark:text-gray-300",
    label: "Cliffhanger",
    code: "C",
  },
  betrayal: {
    bg: "bg-gray-100 dark:bg-gray-800",
    text: "text-gray-700 dark:text-gray-300",
    label: "Betrayal",
    code: "B",
  },
  reveal: {
    bg: "bg-gray-100 dark:bg-gray-800",
    text: "text-gray-700 dark:text-gray-300",
    label: "Reveal",
    code: "V",
  },
  revenge: {
    bg: "bg-gray-100 dark:bg-gray-800",
    text: "text-gray-700 dark:text-gray-300",
    label: "Revenge",
    code: "X",
  },
  reunion: {
    bg: "bg-gray-100 dark:bg-gray-800",
    text: "text-gray-700 dark:text-gray-300",
    label: "Reunion",
    code: "U",
  },
  threat: {
    bg: "bg-gray-100 dark:bg-gray-800",
    text: "text-gray-700 dark:text-gray-300",
    label: "Threat",
    code: "T",
  },
  taboo: {
    bg: "bg-gray-100 dark:bg-gray-800",
    text: "text-gray-700 dark:text-gray-300",
    label: "Taboo",
    code: "N",
  },
  "power-shift": {
    bg: "bg-gray-100 dark:bg-gray-800",
    text: "text-gray-700 dark:text-gray-300",
    label: "Power Shift",
    code: "S",
  },
};

const DEFAULT_STYLE = {
  bg: "bg-gray-100 dark:bg-gray-800",
  text: "text-gray-600 dark:text-gray-400",
  label: "Tag",
  code: "M",
};

interface HookTagBadgeProps {
  /** Hook type: hook/reversal/payoff/cliffhanger/betrayal/reveal/revenge/reunion/threat/taboo/power-shift */
  hookType: string;
  /** Intensity: low/medium/high */
  intensity?: string;
  /** Whether to show the full label (otherwise only the icon is shown) */
  showLabel?: boolean;
  /** Click callback */
  onClick?: () => void;
  /** Additional className */
  className?: string;
}

/**
 * Hook tag badge component
 *
 * Used to display the hook type on storyboard frames (hook/reversal/payoff/cliffhanger, etc.)
 */
export function HookTagBadge({
  hookType,
  intensity,
  showLabel = true,
  onClick,
  className = "",
}: HookTagBadgeProps) {
  const normalizedType = hookType?.toLowerCase().replace(/\s+/g, "-") || "";
  const style = HOOK_STYLES[normalizedType] || DEFAULT_STYLE;

  // Border style for each intensity level
  const intensityBorder =
    intensity === "high"
      ? "ring-2 ring-offset-1 ring-current"
      : intensity === "medium"
      ? "ring-1 ring-current"
      : "";

  return (
    <span
      className={`
        inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium
        ${style.bg} ${style.text} ${intensityBorder}
        ${onClick ? "cursor-pointer hover:opacity-80" : ""}
        ${className}
      `}
      onClick={onClick}
      title={`${style.label}${intensity ? ` (${intensity})` : ""}`}
    >
      <span className="font-mono text-[10px]">{style.code}</span>
      {showLabel && <span>{style.label}</span>}
    </span>
  );
}
