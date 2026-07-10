"use client";

import {
  OperatorAdminShell,
  OperatorPanel,
  OperatorSectionHeader,
  OperatorState,
} from "@/components/shared";

export default function AdminSettingsPage() {
  return (
    <OperatorAdminShell title="System Settings" subtitle="Runtime policies and system configuration">
      <div className="space-y-6">
        <OperatorPanel>
          <OperatorSectionHeader title="System Settings" subtitle="Configuration placeholders and future links" />
          <div className="p-4">
            <OperatorState title="System configuration features are under development" detail="This screen is reserved as the admin configuration entry point." />
            <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {[
                "User Registration Settings",
                "Email Notification Settings",
                "Security Policy Settings",
                "System Log Settings",
                "Backup Settings",
                "Performance Monitoring",
              ].map((setting) => (
                <div
                  key={setting}
                  className="rounded-md border border-gray-200 bg-gray-50 px-4 py-3"
                >
                  <div className="text-sm font-medium text-gray-900">
                    {setting}
                  </div>
                  <div className="mt-1 text-xs text-gray-500">Pending Link</div>
                </div>
              ))}
            </div>
          </div>
        </OperatorPanel>
      </div>
    </OperatorAdminShell>
  );
}
