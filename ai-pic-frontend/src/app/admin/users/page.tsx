"use client";

import { Suspense } from "react";
import { OperatorAdminShell, OperatorState } from "@/components/shared";
import { AdminUsersContent } from "./AdminUsersContent";

export default function AdminUsersPage() {
  return (
    <Suspense
      fallback={
        <OperatorAdminShell title="User Management" subtitle="Registration, approval, and permission status">
          <OperatorState title="Loading user list..." />
        </OperatorAdminShell>
      }
    >
      <AdminUsersContent />
    </Suspense>
  );
}
