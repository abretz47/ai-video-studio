"use client";

import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
  UserApprovalModal,
  UserDetailsModal,
} from "@/components/shared/modals";
import {
  OperatorAdminShell,
  OperatorPanel,
  OperatorSectionHeader,
  OperatorState,
  operatorButtonClass,
  operatorInputClass,
  operatorSelectClass,
} from "@/components/shared";
import { adminAPI } from "@/utils/api/endpoints";
import type { AdminUser, UserListResponse } from "@/utils/api/types";
import { AdminUserPagination, AdminUserRow } from "./AdminUsersRows";

type UserFilters = {
  page: number;
  size: number;
  status_filter?: string;
  role_filter?: string;
  search?: string;
};

export function AdminUsersContent() {
  const searchParams = useSearchParams();
  const [userList, setUserList] = useState<UserListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [processingUsers, setProcessingUsers] = useState<Set<number>>(new Set());
  const [detailUser, setDetailUser] = useState<AdminUser | null>(null);
  const [approvalUser, setApprovalUser] = useState<AdminUser | null>(null);
  const [filters, setFilters] = useState<UserFilters>({
    page: 1,
    size: 20,
    status_filter: searchParams.get("status") || undefined,
    role_filter: searchParams.get("role") || undefined,
  });

  const loadUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await adminAPI.getUsers(filters);
      if (response.success && response.data) setUserList(response.data);
      else setError(response.error || "Failed to fetch user list");
    } catch (err) {
      console.error("Failed to load user list:", err);
      setError("Network error. Please try again later");
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    void loadUsers();
  }, [loadUsers]);

  const verifyEmail = async (user: AdminUser) => {
    setProcessingUsers((prev) => new Set(prev).add(user.id));
    try {
      const response = await adminAPI.updateUserAdmin(user.id, {
        email_verified: true,
      });
      if (response.success) await loadUsers();
      else setError(response.error || "Operation failed");
    } finally {
      setProcessingUsers((prev) => {
        const next = new Set(prev);
        next.delete(user.id);
        return next;
      });
    }
  };

  const updateUser = (updated: AdminUser) => {
    setUserList((prev) =>
      prev
        ? { ...prev, users: prev.users.map((user) => (user.id === updated.id ? updated : user)) }
        : prev,
    );
    setDetailUser((prev) => (prev?.id === updated.id ? updated : prev));
  };

  return (
    <OperatorAdminShell title="User Management" subtitle="Registration, approval, and permission status">
      <div className="space-y-4">
        <OperatorPanel>
          <OperatorSectionHeader
            title="Filters"
            subtitle={userList ? `Total ${userList.total} users` : "Loading user data"}
            action={
              <button
                type="button"
                onClick={() => void loadUsers()}
                className={operatorButtonClass("secondary")}
              >
                Refresh
              </button>
            }
          />
          <div className="grid gap-3 p-4 md:grid-cols-[minmax(0,1fr)_160px_160px]">
            <input
              value={filters.search || ""}
              onChange={(event) =>
                setFilters((prev) => ({ ...prev, page: 1, search: event.target.value || undefined }))
              }
              className={operatorInputClass("w-full")}
              placeholder="Search username, email, or full name"
            />
            <select
              value={filters.status_filter || ""}
              onChange={(event) =>
                setFilters((prev) => ({ ...prev, page: 1, status_filter: event.target.value || undefined }))
              }
              className={operatorSelectClass("w-full")}
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending approval</option>
              <option value="approved">Approved</option>
              <option value="suspended">Paused</option>
              <option value="locked">Locked</option>
            </select>
            <select
              value={filters.role_filter || ""}
              onChange={(event) =>
                setFilters((prev) => ({ ...prev, page: 1, role_filter: event.target.value || undefined }))
              }
              className={operatorSelectClass("w-full")}
            >
              <option value="">All Roles</option>
              <option value="admin">Admin</option>
              <option value="superuser">Super User</option>
              <option value="user">Regular User</option>
            </select>
          </div>
        </OperatorPanel>

        {error ? <OperatorState title={error} tone="red" /> : null}
        {loading && !userList ? <OperatorState title="Loading user list..." /> : null}

        <OperatorPanel>
          <OperatorSectionHeader title="User List" subtitle="Approvals, email verification, and user details" />
          <div className="divide-y divide-gray-100">
            {userList?.users.length ? (
              userList.users.map((user) => (
                <AdminUserRow
                  key={user.id}
                  user={user}
                  processing={processingUsers.has(user.id)}
                  onApprove={() => setApprovalUser(user)}
                  onVerifyEmail={() => void verifyEmail(user)}
                  onDetails={() => setDetailUser(user)}
                />
              ))
            ) : (
              <div className="p-6 text-sm text-gray-500">No users match the current filters.</div>
            )}
          </div>
          {userList && userList.pages > 1 ? (
            <AdminUserPagination
              page={filters.page}
              pages={userList.pages}
              total={userList.total}
              onPage={(page) => setFilters((prev) => ({ ...prev, page }))}
            />
          ) : null}
        </OperatorPanel>
      </div>

      <UserDetailsModal
        user={detailUser}
        isOpen={Boolean(detailUser)}
        onClose={() => setDetailUser(null)}
        onUserUpdate={updateUser}
      />
      <UserApprovalModal
        user={approvalUser}
        isOpen={Boolean(approvalUser)}
        onClose={() => setApprovalUser(null)}
        onApprovalComplete={(user) => updateUser(user)}
      />
    </OperatorAdminShell>
  );
}
