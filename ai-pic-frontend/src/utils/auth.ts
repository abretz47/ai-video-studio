import {
  formatDateTime as formatLocalizedDateTime,
  formatRelativeTime as formatLocalizedRelativeTime,
  t,
} from "@/lib/i18n";
import type { User } from "@/utils/api/types";

export function isAuthenticated(): boolean {
  if (typeof window === "undefined") return false;

  const token = localStorage.getItem("auth_token");
  const userInfo = localStorage.getItem("user_info");

  return !!(token && userInfo);
}

export const isAdmin = (user: User | null): boolean => {
  return user ? user.is_admin || user.is_superuser : false;
};

export const getUserStatus = (user: User): string => {
  if (!user.email_verified) return t("auth.userStatus.pendingEmail", "Pending email verification");
  if (!user.is_approved) return t("auth.userStatus.pendingApproval", "Pending approval");
  if (!user.is_active) return t("auth.userStatus.disabled", "Disabled");
  if (user.is_account_locked) return t("auth.userStatus.locked", "Locked");
  return t("auth.userStatus.normal", "Active");
};

export const getUserRole = (user: User): string => {
  if (user.is_superuser) return t("auth.userRole.superAdmin", "Super admin");
  if (user.is_admin) return t("auth.userRole.admin", "Admin");
  return t("auth.userRole.user", "User");
};

export const formatDateTime = (dateString?: string): string => {
  if (!dateString) return t("common.emptyDash", "—");
  return formatLocalizedDateTime(dateString, {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

export const formatRelativeTime = (dateString?: string): string => {
  if (!dateString) return t("common.emptyDash", "—");
  return formatLocalizedRelativeTime(dateString);
};

export const hasPendingApprovals = (
  stats: { pending_approval: number } | null,
): boolean => {
  return stats ? stats.pending_approval > 0 : false;
};
