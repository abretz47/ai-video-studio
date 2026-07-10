"use client";

import { t } from "@/lib/i18n";
import {
  OperatorPanel,
  OperatorShell,
  operatorButtonClass,
} from "@/components/shared";
import { useStories, type UseStoriesOptions } from "@/hooks/useStories";
import { StoryGenerateForm } from "./StoryGenerateForm";
import { StoryListSection } from "./StoryListSection";

export function StoryProductionBoard({
  showAlert,
}: {
  showAlert: UseStoriesOptions["showAlert"];
}) {
  const state = useStories({ showAlert });
  const {
    stories,
    virtualIPs,
    loading,
    generating,
    showGenerateForm,
    generateForm,
    setGenerateForm,
    promptPreview,
    showPromptPreview,
    useAsync,
    setUseAsync,
    selectedGenre,
    setSelectedGenre,
    selectedStatus,
    setSelectedStatus,
    handleGenerateStory,
    handleDeleteStory,
    handleCharacterToggle,
    handlePreviewPrompt,
    openGenerateForm,
    closeGenerateForm,
    navigateToVirtualIP,
  } = state;

  return (
    <OperatorShell
      title={t("stories.board.title", "IP Story Production")}
      subtitle={t("stories.board.subtitle", "Organize stories, episodes, and generation prep around each IP")}
      breadcrumb={[
        t("common.breadcrumb.ipCenter", "IP Center"),
        t("stories.board.breadcrumb", "Story Production"),
      ]}
    >
      <div className="space-y-5">
        <OperatorPanel className="p-4">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <h2 className="text-sm font-semibold text-gray-950">{t("stories.board.entryTitle", "Story entry")}</h2>
              <p className="mt-1 text-xs text-gray-500">
                {t(
                  "stories.board.entryDescription",
                  "Stories connect IP characters, environment assets, and episode production. Continue readiness checks and episode generation from the detail page.",
                )}
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={openGenerateForm}
                className={operatorButtonClass("primary")}
              >
                {t("stories.board.createFromIp", "Create from IP")}
              </button>
            </div>
          </div>
        </OperatorPanel>

        <StoryListSection
          stories={stories}
          loading={loading}
          selectedGenre={selectedGenre}
          onSelectedGenreChange={setSelectedGenre}
          selectedStatus={selectedStatus}
          onSelectedStatusChange={setSelectedStatus}
          onOpenGenerateForm={openGenerateForm}
          onDelete={handleDeleteStory}
        />
      </div>

      <StoryGenerateForm
        open={showGenerateForm}
        onClose={closeGenerateForm}
        virtualIPs={virtualIPs}
        generateForm={generateForm}
        setGenerateForm={setGenerateForm}
        promptPreview={promptPreview}
        showPromptPreview={showPromptPreview}
        useAsync={useAsync}
        setUseAsync={setUseAsync}
        generating={generating}
        onCharacterToggle={handleCharacterToggle}
        onPreviewPrompt={handlePreviewPrompt}
        onSubmit={handleGenerateStory}
        onNavigateToVirtualIP={navigateToVirtualIP}
      />
    </OperatorShell>
  );
}
