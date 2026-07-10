"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  AuthGuard,
  OperatorPanel,
  OperatorSectionHeader,
  OperatorShell,
  operatorButtonClass,
} from "@/components/shared";
import {
  EnvironmentCreateOverlay,
  EnvironmentList,
} from "@/components/features";
import { storyStructureAPI } from "@/utils/api/endpoints";
import type { Environment } from "@/utils/api/types";
import { useAlertModal } from "@/components/shared/modals/AlertModalProvider";

function EnvironmentsPageContent() {
  const router = useRouter();
  const { showAlert } = useAlertModal();
  const [list, setList] = useState<Environment[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const res = await storyStructureAPI.listEnvironments();
      if (res.success && res.data) {
        setList(res.data);
      } else {
        showAlert({ message: res.error || "Failed to load environments", variant: "error" });
      }
    } catch (e) {
      console.error(e);
      showAlert({ message: "Failed to load environments", variant: "error" });
    } finally {
      setLoading(false);
    }
  }, [showAlert]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleDelete = (env: Environment) => {
    showAlert({
      title: "Confirm Environment Deletion",
      message: "After deletion, scenes that reference this environment will lose the link. Are you sure you want to delete it?",
      variant: "warning",
      confirmText: "Delete",
      onConfirm: async () => {
        try {
          const res = await storyStructureAPI.deleteEnvironment(env.id);
          if (res.success) {
            setList((prev) => prev.filter((item) => item.id !== env.id));
            showAlert({ message: "Deleted successfully", variant: "success" });
          } else {
            showAlert({ message: res.error || "Deletion failed", variant: "error" });
          }
        } catch (e) {
          console.error(e);
          showAlert({ message: "Deletion failed", variant: "error" });
        }
      },
    });
  };

  return (
    <OperatorShell
      title="Environment Assets"
      subtitle="Maintain reusable environments for Virtual IP, story, and episode scenes"
      breadcrumb={["IP Hub", "Environment Assets"]}
    >
      <OperatorPanel className="mb-5">
        <OperatorSectionHeader
          title="Environment Assets"
          subtitle="These can be added directly to the Virtual IP environment pool or bound to scenes on an episode timeline"
          action={
            <div className="flex gap-2">
              <button
                onClick={() => setShowCreateForm(true)}
                className={operatorButtonClass("primary")}
              >
                Create Environment
              </button>
              <button
                onClick={() => void load()}
                className={operatorButtonClass("secondary")}
              >
                Refresh
              </button>
            </div>
          }
        />
      </OperatorPanel>

      <EnvironmentList
        loading={loading}
        list={list}
        onRefresh={() => void load()}
        onManage={(env) =>
          router.push(`/environments/${env.business_id || env.id}`)
        }
        onDelete={handleDelete}
      />

      <EnvironmentCreateOverlay
        open={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onCreated={(env) => setList((prev) => [env, ...prev])}
      />
    </OperatorShell>
  );
}

export default function EnvironmentsPage() {
  return (
    <AuthGuard>
      <EnvironmentsPageContent />
    </AuthGuard>
  );
}
