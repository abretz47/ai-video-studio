"use client";

import { formatDateOnly, t } from "@/lib/i18n";
import {
  OperatorPanel,
  OperatorSectionHeader,
  OperatorState,
  StatusPill,
  operatorButtonClass,
} from "@/components/shared";
import type { Environment } from "@/utils/api/types";
import { resolveCreatorLabel } from "@/utils/creator";

interface EnvironmentListProps {
  loading: boolean;
  list: Environment[];
  onRefresh: () => void;
  onManage: (env: Environment) => void;
  onDelete: (env: Environment) => void;
}

export function EnvironmentList({
  loading,
  list,
  onRefresh,
  onManage,
  onDelete,
}: EnvironmentListProps) {
  return (
    <OperatorPanel>
      <OperatorSectionHeader
        title={t("environments.list.title", "Environment List")}
        subtitle={t("environments.list.subtitle", "Scene asset pool reused across IP projects")}
        action={
          <button
            type="button"
            onClick={onRefresh}
            className={operatorButtonClass("secondary")}
          >
            {t("common.refresh", "Refresh")}
          </button>
        }
      />
      {loading ? (
        <div className="p-4">
          <OperatorState title={t("environments.list.loading", "Loading environment assets...")} />
        </div>
      ) : list.length === 0 ? (
        <div className="p-4">
          <OperatorState
            title={t("environments.list.emptyTitle", "No environment assets yet")}
            detail={t("environments.list.emptyDetail", "Create one to manage images from the detail view.")}
          />
        </div>
      ) : (
        <div className="grid gap-3 p-4 md:grid-cols-2 xl:grid-cols-3">
          {list.map((env) => (
            <article
              key={env.id}
              className="rounded-lg border border-gray-200 bg-white p-4"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <h3 className="truncate text-sm font-semibold text-gray-950">
                    {env.name}
                  </h3>
                  <p className="mt-1 text-xs text-gray-500">
                    {resolveCreatorLabel(env.creator)} ·{" "}
                    {formatDateOnly(env.created_at)}
                  </p>
                </div>
                <StatusPill tone={(env.linked_virtual_ip_count || 0) > 0 ? "green" : "amber"}>
                  {(env.linked_virtual_ip_count || 0) > 0
                    ? t("environments.list.linkedIpCount", "{count} linked IPs").replace("{count}", String(env.linked_virtual_ip_count || 0))
                    : t("environments.list.unlinked", "No linked IP")}
                </StatusPill>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => onManage(env)}
                    className={operatorButtonClass(
                      "ghost",
                      "whitespace-nowrap",
                    )}
                  >
                    {t("environments.list.manageImages", "Manage Images")}
                  </button>
                  <button
                    type="button"
                    onClick={() => onDelete(env)}
                    className="h-8 rounded-md px-2 text-xs font-medium text-red-600 hover:bg-red-50 whitespace-nowrap"
                  >
                    {t("common.delete", "Delete")}
                  </button>
                </div>
              </div>

              <div className="mt-3 text-xs text-gray-500">
                {t("common.category", "Category")}: {env.category || t("common.unspecified", "Unspecified")}
              </div>
              {env.tags && env.tags.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {env.tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-md border border-gray-200 bg-gray-50 px-2 py-1 text-xs text-gray-600"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
              {env.linked_virtual_ips && env.linked_virtual_ips.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {env.linked_virtual_ips.slice(0, 3).map((ip) => (
                    <span
                      key={ip.id}
                      className="rounded-md border border-blue-100 bg-blue-50 px-2 py-1 text-xs text-blue-700"
                    >
                      IP: {ip.name}
                    </span>
                  ))}
                </div>
              )}
              {env.description && (
                <p className="mt-3 line-clamp-3 text-sm leading-6 text-gray-600">
                  {env.description}
                </p>
              )}
            </article>
          ))}
        </div>
      )}
    </OperatorPanel>
  );
}
