"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  OperatorAdminShell,
  OperatorPanel,
  OperatorSectionHeader,
  OperatorState,
  StatusPill,
  operatorButtonClass,
} from "@/components/shared";
import { adminAPI } from "@/utils/api/endpoints";
import type { UserStatsResponse } from "@/utils/api/types";

const statItems = (stats: UserStatsResponse) => [
  { label: "Total Users", value: stats.total_users, href: "/admin/users" },
  { label: "ActiveUser", value: stats.active_users, href: "/admin/users?status=approved" },
  { label: "Pending approval", value: stats.pending_approval, href: "/admin/users?status=pending", tone: "amber" as const },
  { label: "Pause User", value: stats.suspended_users, href: "/admin/users?status=suspended", tone: "red" as const },
  { label: "Admin", value: stats.admin_users, href: "/admin/users?role=admin", tone: "blue" as const },
  { label: "Recent Registrations", value: stats.recent_registrations, tone: "green" as const },
];

export default function AdminStatsPage() {
  const [stats, setStats] = useState<UserStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await adminAPI.getUserStats();
      if (response.success && response.data) setStats(response.data);
      else setError(response.error || "Failed to fetch statistics");
    } catch (err) {
      console.error("Failed to load statistics:", err);
      setError("Network error. Please try again later");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadStats();
  }, []);

  return (
    <OperatorAdminShell title="Statistics" subtitle="User and approval operations overview">
      <div className="space-y-4">
        <OperatorPanel>
          <OperatorSectionHeader
            title="User Statistics"
            subtitle="Account, approval, and permission distribution"
            action={
              <button
                type="button"
                onClick={() => void loadStats()}
                className={operatorButtonClass("secondary")}
              >
                Refresh
              </button>
            }
          />
          {loading ? <div className="p-4"><OperatorState title="Loading statistics..." /></div> : null}
          {error ? <div className="p-4"><OperatorState title={error} tone="red" /></div> : null}
          {stats ? (
            <div className="grid gap-3 p-4 md:grid-cols-3">
              {statItems(stats).map((item) => {
                const card = (
                  <div className="rounded-md border border-gray-200 bg-gray-50 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-xs text-gray-500">{item.label}</span>
                      <StatusPill tone={item.tone || "gray"}>{item.value}</StatusPill>
                    </div>
                    <div className="mt-3 text-2xl font-semibold text-gray-950">
                      {item.value.toLocaleString()}
                    </div>
                  </div>
                );
                return item.href ? (
                  <Link key={item.label} href={item.href} className="block hover:opacity-90">
                    {card}
                  </Link>
                ) : (
                  <div key={item.label}>{card}</div>
                );
              })}
            </div>
          ) : null}
        </OperatorPanel>
        {stats ? (
          <OperatorPanel>
            <OperatorSectionHeader title="Quick Actions" subtitle="Jump from statistics to user processing" />
            <div className="grid gap-3 p-4 md:grid-cols-3">
              <QuickLink href="/admin/users?status=pending" label="Handle Pending Approval" detail={`${stats.pending_approval}Pending`} />
              <QuickLink href="/admin/users" label="Manage Users" detail="View all accounts" />
              <QuickLink href="/admin/users?role=admin" label="Admin Permissions" detail={`${stats.admin_users}Admin Accounts`} />
            </div>
          </OperatorPanel>
        ) : null}
      </div>
    </OperatorAdminShell>
  );
}

function QuickLink({
  href,
  label,
  detail,
}: {
  href: string;
  label: string;
  detail: string;
}) {
  return (
    <Link
      href={href}
      className="rounded-md border border-gray-200 bg-white p-4 text-sm hover:border-gray-300 hover:bg-gray-50"
    >
      <div className="font-medium text-gray-950">{label}</div>
      <div className="mt-1 text-xs text-gray-500">{detail}</div>
    </Link>
  );
}
