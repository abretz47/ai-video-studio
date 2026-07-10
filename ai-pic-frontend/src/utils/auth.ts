// Authentication utility functions
import type { User } from "@/utils/api/types";

/**
 * Check whether the user is signed in
 */
export function isAuthenticated(): boolean {
  if (typeof window === "undefined") return false;

  const token = localStorage.getItem("auth_token");
  const userInfo = localStorage.getItem("user_info");

  return !!(token && userInfo);
}

/**
 * Check whether the user has admin privileges
 */
export const isAdmin = (user: User | null): boolean => {
  return user ? user.is_admin || user.is_superuser : false;
};

/**
 * Get the display text for user status
 */
export const getUserStatus = (user: User): string => {
  if (!user.email_verified) return "Pending email verification";
  if (!user.is_approved) return "Pending approval";
  if (!user.is_active) return "Disabled";
  if (user.is_account_locked) return "Locked";
  return "Active";
};

/**
 * Get the display text for user role
 */
export const getUserRole = (user: User): string => {
  if (user.is_superuser) return "Super Admin";
  if (user.is_admin) return "Admin";
  return "Standard User";
};

/**
 * Format the time for display
 */
const formatDateTime = (dateString?: string): string => {
  if (!dateString) return "-";

  const date = new Date(dateString);
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
};

/**
 * Format relative time
 */
export const formatRelativeTime = (dateString?: string): string => {
  if (!dateString) return "-";

  const date = new Date(dateString);
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();

  const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
  const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

  if (diffInMinutes < 1) return "Just now";
  if (diffInMinutes < 60) return `${diffInMinutes} minute${diffInMinutes === 1 ? "" : "s"} ago`;
  if (diffInHours < 24) return `${diffInHours} hour${diffInHours === 1 ? "" : "s"} ago`;
  if (diffInDays < 7) return `${diffInDays} day${diffInDays === 1 ? "" : "s"} ago`;

  return formatDateTime(dateString);
};

/**
 * Check whether there are pending user approvals
 */
export const hasPendingApprovals = (
  stats: { pending_approval: number } | null,
): boolean => {
  return stats ? stats.pending_approval > 0 : false;
};
