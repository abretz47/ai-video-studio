"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { t } from "@/lib/i18n";
import {
  OperatorPanel,
  OperatorMainCanvas,
  OperatorShell,
  OperatorState,
  OperatorWorkspace,
  operatorButtonClass,
} from "@/components/shared";
import { useAlertModal } from "@/components/shared/modals/AlertModalProvider";
import {
  VirtualIPAdditionalInfoSection,
  VirtualIPEnvironmentPanel,
  VirtualIPInfoSection,
  VirtualIPImageManager,
  VoiceSettingsPanel,
} from "@/components/features";
import { VirtualIPReadinessWarnings } from "@/components/features/virtual-ip-detail/VirtualIPReadinessWarnings";
import { useVirtualIPDetail } from "@/hooks/useVirtualIPDetail";
import {
  VirtualIPBackgroundStorySection,
  VirtualIPInspectorPanel,
  VirtualIPMetaStrip,
  VirtualIPProductionNotice,
} from "./VirtualIPDetailPageParts";

export default function VirtualIPDetail() {
  const params = useParams();
  const router = useRouter();
  const { showAlert } = useAlertModal();
  const ipKey = params?.id?.toString() || "";
  const editFormId = "virtual-ip-edit-form";
  const [linkedEnvironmentCount, setLinkedEnvironmentCount] = useState(0);
  const state = useVirtualIPDetail({ ipKey, showAlert, router });
  const {
    virtualIP,
    loading,
    editing,
    setEditing,
    editForm,
    setEditForm,
    voiceEnums,
    voiceTypeFilter,
    setVoiceTypeFilter,
    voiceSettings,
    setVoiceSettings,
    voicePreviewText,
    setVoicePreviewText,
    voiceLoading,
    previewLoading,
    previewAudioUrl,
    voiceOptions,
    handleUpdateIP,
    handleDeleteIP,
    addTag,
    removeTag,
    handlePreviewVoice,
  } = state;

  if (loading) {
    return (
      <OperatorShell
        title={t("virtualIp.detail.pageTitle", "IP Details")}
        subtitle={t("virtualIp.detail.loadingSubtitle", "Loading IP assets...")}
        breadcrumb={[
          t("common.breadcrumb.ipCenter", "IP Center"),
          t("virtualIp.page.breadcrumb", "IP Projects"),
          t("common.loading", "Loading")
        ]}
      >
        <OperatorState title={t("virtualIp.list.loading", "Loading IP assets...")} />
      </OperatorShell>
    );
  }

  if (!virtualIP) {
    return (
      <OperatorShell
        title={t("virtualIp.detail.pageTitle", "IP Details")}
        subtitle={t("virtualIp.page.subtitle", "IP assets are the starting point for stories, episodes, and generation tasks")}
        breadcrumb={[
          t("common.breadcrumb.ipCenter", "IP Center"),
          t("virtualIp.page.breadcrumb", "IP Projects")
        ]}
      >
        <OperatorState
          title={t("virtualIp.detail.notFound", "IP not found")}
          tone="red"
          action={
            <Link
              href="/virtual-ip"
              className={operatorButtonClass("secondary")}
            >
              {t("virtualIp.detail.backToProjects", "Back to IP projects")}
            </Link>
          }
        />
      </OperatorShell>
    );
  }

  return (
    <OperatorShell
      title={t("virtualIp.detail.pageTitle", "IP Details")}
      subtitle={t("virtualIp.page.subtitle", "IP assets are the starting point for stories, episodes, and generation tasks")}
      breadcrumb={[
        t("common.breadcrumb.ipCenter", "IP Center"),
        t("virtualIp.page.breadcrumb", "IP Projects"),
        virtualIP.name,
      ]}
    >
      <div className="space-y-5">
        <VirtualIPProductionNotice />
        <VirtualIPReadinessWarnings readiness={virtualIP.readiness} />

        <OperatorWorkspace
          variant="main-inspector"
          main={
            <OperatorMainCanvas>
              <OperatorPanel>
                <VirtualIPInfoSection
                  virtualIP={virtualIP}
                  editing={editing}
                  editForm={editForm}
                  setEditForm={setEditForm}
                  onSubmit={handleUpdateIP}
                  addTag={addTag}
                  removeTag={removeTag}
                  formId={editFormId}
                />
                <VirtualIPBackgroundStorySection
                  virtualIP={virtualIP}
                  editing={editing}
                  editForm={editForm}
                  setEditForm={setEditForm}
                />
                <VirtualIPAdditionalInfoSection
                  virtualIP={virtualIP}
                  editing={editing}
                  editForm={editForm}
                  setEditForm={setEditForm}
                />
                <VoiceSettingsPanel
                  editing={editing}
                  voiceEnums={voiceEnums}
                  voiceTypeFilter={voiceTypeFilter}
                  setVoiceTypeFilter={setVoiceTypeFilter}
                  voiceSettings={voiceSettings}
                  setVoiceSettings={setVoiceSettings}
                  voicePreviewText={voicePreviewText}
                  setVoicePreviewText={setVoicePreviewText}
                  voiceLoading={voiceLoading}
                  previewLoading={previewLoading}
                  previewAudioUrl={previewAudioUrl}
                  voiceOptions={voiceOptions}
                  onPreviewVoice={handlePreviewVoice}
                />
                <VirtualIPMetaStrip virtualIP={virtualIP} />
              </OperatorPanel>
              <div className="mt-5">
                <VirtualIPEnvironmentPanel
                  virtualIP={virtualIP}
                  onLinkedCountChange={setLinkedEnvironmentCount}
                />
              </div>
            </OperatorMainCanvas>
          }
          inspector={<VirtualIPInspectorPanel
            virtualIP={virtualIP}
            editing={editing}
            editFormId={editFormId}
            linkedEnvironmentCount={linkedEnvironmentCount}
            setEditing={setEditing}
            onDelete={handleDeleteIP}
          />}
        />

        <VirtualIPImageManager virtualIPKey={ipKey} virtualIP={virtualIP} />
      </div>
    </OperatorShell>
  );
}
