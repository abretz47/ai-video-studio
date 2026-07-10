"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { t } from "@/lib/i18n";
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
        showAlert({ message: res.error || t("environments.page.loadFailed", "Failed to load environments"), variant: "error" });
      }
    } catch (e) {
      console.error(e);
      showAlert({ message: t("environments.page.loadFailed", "Failed to load environments"), variant: "error" });
    } finally {
      setLoading(false);
    }
  }, [showAlert]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleDelete = (env: Environment) => {
    showAlert({
      title: t("environments.page.confirmDeleteTitle", "Confirm environment deletion"),
      message: t("environments.page.confirmDeleteMessage", "Scenes that reference this environment will lose their link after deletion. Continue?") ,
      variant: "warning",
      confirmText: t("common.delete", "Delete"),
      onConfirm: async () => {
        try {
          const res = await storyStructureAPI.deleteEnvironment(env.id);
          if (res.success) {
            setList((prev) => prev.filter((item) => item.id !== env.id));
            showAlert({ message: t("common.deleteSuccess", "Deleted successfully"), variant: "success" });
          } else {
            showAlert({ message: res.error || t("common.deleteFailed", "Delete failed"), variant: "error" });
          }
        } catch (e) {
          console.error(e);
          showAlert({ message: t("common.deleteFailed", "Delete failed"), variant: "error" });
        }
      },
    });
  };

  return (
    <OperatorShell
      title={t("environments.page.title", "Environment Assets")}
      subtitle={t("environments.page.subtitle", "Maintain reusable environments for IPs, stories, and episode scenes")}
      breadcrumb={[
        t("common.breadcrumb.ipCenter", "IP Center"),
        t("environments.page.breadcrumb", "Environment Assets"),
      ]}
    >
      <OperatorPanel className="mb-5">
        <OperatorSectionHeader
          title={t("environments.page.headerTitle", "Environment Assets")}
          subtitle={t("environments.page.headerSubtitle", "Add directly to the IP environment pool or bind them to scenes from an episode timeline")}
          action={
            <div className="flex gap-2">
              <button
                onClick={() => setShowCreateForm(true)}
                className={operatorButtonClass("primary")}
              >
                {t("environments.page.create", "Create Environment")}
              </button>
              <button
                onClick={() => void load()}
                className={operatorButtonClass("secondary")}
              >
                {t("common.refresh", "Refresh")}
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
