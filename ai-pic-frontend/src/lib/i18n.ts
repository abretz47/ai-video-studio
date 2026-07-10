import enMessages from "@/locales/en.json";
import zhMessages from "@/locales/zh.json";

const DEFAULT_LOCALE = "en";
const RAW_LOCALE = process.env.NEXT_PUBLIC_LOCALE?.trim() || DEFAULT_LOCALE;
const IS_ZH = /^zh([_-].+)?$/i.test(RAW_LOCALE);

export const locale = IS_ZH ? "zh-CN" : "en";
export const displayLocale = locale;

type Messages = Record<string, string>;

const messages: Messages = IS_ZH ? (zhMessages as Messages) : (enMessages as Messages);

export function t(key: string, fallback = ""): string {
  const value = messages[key];
  if (typeof value === "string" && value.length > 0) {
    return value;
  }
  if (fallback.length > 0) {
    return fallback;
  }
  return key;
}

function parseDate(input?: string): Date | null {
  if (!input) return null;
  const parsed = new Date(input);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

export function formatDateTime(
  input?: string,
  options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  },
): string {
  const value = parseDate(input);
  if (!value) return "—";
  return new Intl.DateTimeFormat(displayLocale, options).format(value);
}

export function formatDateOnly(
  input?: string,
  options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  },
): string {
  const value = parseDate(input);
  if (!value) return "—";
  return new Intl.DateTimeFormat(displayLocale, options).format(value);
}

export function formatRelativeTime(input?: string): string {
  const value = parseDate(input);
  if (!value) return "—";

  const diffMs = value.getTime() - Date.now();
  const diffSeconds = Math.round(diffMs / 1000);
  const absSeconds = Math.abs(diffSeconds);

  const rtf = new Intl.RelativeTimeFormat(displayLocale, { numeric: "auto" });

  if (absSeconds < 60) return rtf.format(diffSeconds, "second");

  const diffMinutes = Math.round(diffSeconds / 60);
  if (Math.abs(diffMinutes) < 60) return rtf.format(diffMinutes, "minute");

  const diffHours = Math.round(diffMinutes / 60);
  if (Math.abs(diffHours) < 24) return rtf.format(diffHours, "hour");

  const diffDays = Math.round(diffHours / 24);
  if (Math.abs(diffDays) < 30) return rtf.format(diffDays, "day");

  const diffMonths = Math.round(diffDays / 30);
  if (Math.abs(diffMonths) < 12) return rtf.format(diffMonths, "month");

  const diffYears = Math.round(diffDays / 365);
  return rtf.format(diffYears, "year");
}
