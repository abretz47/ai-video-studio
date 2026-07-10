"use client";

import { t } from "@/lib/i18n";
import { AuthGuard, OperatorPanel, OperatorShell } from "@/components/shared";
import { useAlertModal } from "@/components/shared/modals/AlertModalProvider";
import {
  VirtualIPCreateModal,
  VirtualIPListSection,
} from "@/components/features";
import { useVirtualIPCreateForm } from "@/hooks/useVirtualIPCreateForm";
import { useVirtualIPList } from "@/hooks/useVirtualIPList";

function VirtualIPListContent() {
  const { showAlert } = useAlertModal();
  const {
    virtualIPs,
    loading,
    searchTerm,
    setSearchTerm,
    selectedTags,
    toggleTag,
    allTags,
    handleDeleteIP,
    prependVirtualIP,
  } = useVirtualIPList({ showAlert });

  const {
    showCreateForm,
    setShowCreateForm,
    aiGenerating,
    aiBrief,
    setAiBrief,
    formState,
    setFormState,
    handleCreateIP,
    addTag,
    removeTag,
    runGenerateAllAI,
    handleCloseCreateForm,
  } = useVirtualIPCreateForm({ showAlert, onCreated: prependVirtualIP });

  return (
    <OperatorShell
      title={t("virtualIp.page.title", "IP Projects")}
      subtitle={t("virtualIp.page.subtitle", "IP assets are the starting point for stories, episodes, and generation tasks")}
      breadcrumb={[
        t("common.breadcrumb.ipCenter", "IP Center"),
        t("virtualIp.page.breadcrumb", "IP Projects"),
      ]}
    >
      <OperatorPanel className="mb-5 p-4">
        <h2 className="text-sm font-semibold text-gray-950">{t("virtualIp.page.entryTitle", "Production entry")}</h2>
        <p className="mt-1 text-xs text-gray-500">
          {t("virtualIp.page.entryDescription", "Use IP assets to organize characters, stories, and episodes. New stories should select character assets from here first.")}
        </p>
      </OperatorPanel>

      <VirtualIPListSection
        loading={loading}
        virtualIPs={virtualIPs}
        searchTerm={searchTerm}
        onSearchTermChange={setSearchTerm}
        allTags={allTags}
        selectedTags={selectedTags}
        onToggleTag={toggleTag}
        onOpenCreate={() => setShowCreateForm(true)}
        onDelete={handleDeleteIP}
      />

      <VirtualIPCreateModal
        open={showCreateForm}
        onClose={handleCloseCreateForm}
        onSubmit={handleCreateIP}
        showAlert={showAlert}
        aiBrief={aiBrief}
        setAiBrief={setAiBrief}
        aiGenerating={aiGenerating}
        onGenerateAI={runGenerateAllAI}
        formState={formState}
        setFormState={setFormState}
        addTag={addTag}
        removeTag={removeTag}
      />
    </OperatorShell>
  );
}

export default function VirtualIPList() {
  return (
    <AuthGuard>
      <VirtualIPListContent />
    </AuthGuard>
  );
}
