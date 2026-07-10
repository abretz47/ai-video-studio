"use client";

import { useParams, useRouter } from "next/navigation";
import { useAlertModal } from "@/components/shared/modals/AlertModalProvider";
import {
  ScriptHeader,
  WorkflowSteps,
  ScriptOverviewTab,
  ScriptScenesTab,
  ScriptTrafficTab,
} from "@/components/features";
import {
  OperatorShell,
  OperatorState,
  OperatorTabs,
} from "@/components/shared";
import { useScriptDetail, TABS } from "@/hooks/useScriptDetail";
import { episodeWorkspaceHref } from "@/utils/routes";

export default function ScriptDetailPage() {
  const router = useRouter();
  const { id } = useParams();
  const scriptKey = (id as string) || "";
  const { showAlert } = useAlertModal();

  const state = useScriptDetail({ scriptKey, showAlert });

  const {
    activeTab,
    setActiveTab,
    script,
    setStructuredScenes,
    structureLoading,
    structureError,
    showStructureEditor,
    setShowStructureEditor,
    loading,
    showExportMenu,
    setShowExportMenu,
    focusedScene,
    setFocusedScene,
    scenes,
    dialogues,
    directions,
    activeScene,
    selectedNormalizedScene,
    sceneBeats,
    sceneShots,
    canEditStructure,
    handleExport,
    goToSceneDetails,
    goToSceneStructure,
  } = state;

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100">
        <OperatorState title="Loading script..." />
      </div>
    );
  }

  if (!script) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100">
        <OperatorState
          title="Script not found"
          tone="red"
          action={
            <button
              onClick={() => router.push("/stories")}
              className="text-xs font-medium text-red-700 underline"
            >
              Back to Stories
            </button>
          }
        />
      </div>
    );
  }

  return (
    <OperatorShell
      title="Script Details"
      subtitle={script.title}
      breadcrumb={["IP Hub", "Scripts", script.title]}
    >
      <div className="space-y-4">
        <ScriptHeader
          script={script}
          showExportMenu={showExportMenu}
          setShowExportMenu={setShowExportMenu}
          onExport={handleExport}
          onNavigateToEpisode={() =>
            router.push(
              episodeWorkspaceHref(
                script.episode_business_id || script.episode_id,
                {
                  tab: "script",
                  scriptId: script.id,
                },
              ),
            )
          }
          onNavigateToTimeline={() =>
            router.push(
              episodeWorkspaceHref(
                script.episode_business_id || script.episode_id,
                {
                  tab: "timeline",
                  scriptId: script.id,
                },
              ),
            )
          }
        />

        <WorkflowSteps
          onGoToSceneDetails={goToSceneDetails}
          onGoToSceneStructure={goToSceneStructure}
          onGoToTimelineSupport={() =>
            router.push(
              episodeWorkspaceHref(
                script.episode_business_id || script.episode_id,
                {
                  tab: "timeline",
                  scriptId: script.id,
                },
              ),
            )
          }
        />

        <OperatorTabs
          tabs={TABS.map((tab) => ({ key: tab.id, label: tab.name }))}
          active={activeTab}
          onChange={setActiveTab}
        />

        {activeTab === "overview" && (
          <ScriptOverviewTab
            script={script}
            scenes={scenes}
            dialogues={dialogues}
            directions={directions}
          />
        )}

        {activeTab === "scenes" && (
          <ScriptScenesTab
            script={script}
            scenes={scenes}
            dialogues={dialogues}
            directions={directions}
            focusedScene={focusedScene}
            setFocusedScene={setFocusedScene}
            activeScene={activeScene}
            selectedNormalizedScene={selectedNormalizedScene}
            sceneBeats={sceneBeats}
            sceneShots={sceneShots}
            structureLoading={structureLoading}
            structureError={structureError}
            showStructureEditor={showStructureEditor}
            setShowStructureEditor={setShowStructureEditor}
            canEditStructure={canEditStructure}
            setStructuredScenes={setStructuredScenes}
          />
        )}

        {activeTab === "traffic" && <ScriptTrafficTab script={script} />}
      </div>
    </OperatorShell>
  );
}
