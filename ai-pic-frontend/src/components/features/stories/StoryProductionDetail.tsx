"use client";

import Link from "next/link";
import { t } from "@/lib/i18n";
import {
  OperatorPanel,
  OperatorInspector,
  OperatorMainCanvas,
  OperatorSectionHeader,
  OperatorState,
  OperatorWorkspace,
  StatusPill,
  operatorButtonClass,
  operatorTableClass,
  operatorTableHeadClass,
  operatorTableRowClass,
} from "@/components/shared";
import { useAlertModal } from "@/components/shared/modals/AlertModalProvider";
import { EpisodeGeneratePanel } from "@/components/features/story-detail/EpisodeGeneratePanel";
import { StoryReadinessPanel } from "@/components/features/story-detail/StoryReadinessPanel";
import { useStoryDetail } from "@/hooks/useStoryDetail";
import { episodeWorkspaceHref } from "@/utils/routes";
import {
  formatStoryTime,
  hasStoryboard,
  hasTimeline,
  latestScript,
  storyDisplayText,
} from "./StoryProductionModel";
import { CharacterChip, ReadyCell, StoryEnvironmentCoverage } from "./StoryProductionDetailParts";
import { useEpisodeGenerationAnchor } from "./useEpisodeGenerationAnchor";

export function StoryProductionDetail({ storyKey }: { storyKey: string }) {
  const { showAlert } = useAlertModal();
  const state = useStoryDetail({ storyKey, showAlert });
  const {
    story,
    episodes,
    scriptsByEpisode,
    timelinesByEpisode,
    loading,
    loadingScripts,
    genOpen,
    setGenOpen,
    genForm,
    setGenForm,
    promptPreview,
    useAsync,
    setUseAsync,
    includeContinuityLedger,
    setIncludeContinuityLedger,
    includeCharacterCards,
    setIncludeCharacterCards,
    recentEpisodesCount,
    setRecentEpisodesCount,
    contextPackPreview,
    contextPackLoading,
    contextPackError,
    handlePreviewPrompt,
    handlePreviewContextPack,
    handleGenerateEpisodes,
    episodesTask,
    readiness,
    readinessLoading,
    readinessError,
    quickFixLoading,
    canGenerate,
    checkReadiness,
    runQuickFix,
    storyEnvironmentLinks,
  } = state;
  const openEpisodeGeneration = useEpisodeGenerationAnchor(setGenOpen);

  if (loading) {
    return <OperatorState title={t("stories.detail.loading", "Loading story details...")} />;
  }

  if (!story) {
    return <OperatorState title={t("stories.detail.notFound", "Story not found or access denied.")} tone="red" />;
  }

  const linkedCharacters = story.story_characters || story.characters || [];

  return (
    <OperatorWorkspace
      variant="main-inspector"
      main={
        <OperatorMainCanvas className="space-y-5">
          <OperatorPanel className="p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-lg font-semibold text-gray-950">
                    {story.title}
                  </h1>
                  <StatusPill tone="green">{story.status}</StatusPill>
                </div>
                <div className="mt-2 flex flex-wrap gap-2 text-xs text-gray-500">
                  <span>{story.genre}</span>
                  {story.theme ? <span>{story.theme}</span> : null}
                  {story.duration_minutes ? (
                    <span>{story.duration_minutes} {t("common.minutes", "minutes")}</span>
                  ) : null}
                  <span>{t("common.updatedPrefix", "Updated")} {formatStoryTime(story.updated_at)}</span>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={openEpisodeGeneration}
                  className={operatorButtonClass(
                    "primary",
                    "whitespace-nowrap",
                  )}
                >
                  {t("stories.list.generateEpisodes", "Generate episodes")}
                </button>
                <button className={operatorButtonClass("secondary")}>
                  {t("stories.detail.editStory", "Edit story")}
                </button>
              </div>
            </div>
            <p className="mt-4 line-clamp-6 max-w-3xl text-sm leading-6 text-gray-700">
              {storyDisplayText(story.synopsis, story.premise)}
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {linkedCharacters.length ? (
                linkedCharacters.map((character) => (
                  <CharacterChip key={character.id} character={character} />
                ))
              ) : (
                <span className="rounded-md border border-amber-200 bg-amber-50 px-2 py-1 text-xs text-amber-700">
                  {t("stories.list.noLinkedIp", "No linked IP yet")}
                </span>
              )}
              <StoryEnvironmentCoverage links={storyEnvironmentLinks} />
            </div>
          </OperatorPanel>

          <OperatorPanel id="episode-generation" className="scroll-mt-24 p-5">
            <EpisodeGeneratePanel
              genOpen={genOpen}
              setGenOpen={setGenOpen}
              genForm={genForm}
              setGenForm={setGenForm}
              useAsync={useAsync}
              setUseAsync={setUseAsync}
              promptPreview={promptPreview}
              onPreviewPrompt={handlePreviewPrompt}
              onGenerate={handleGenerateEpisodes}
              canGenerate={canGenerate}
              episodesTask={episodesTask}
              contextPackPreviewProps={{
                includeContinuityLedger,
                setIncludeContinuityLedger,
                includeCharacterCards,
                setIncludeCharacterCards,
                recentEpisodesCount,
                setRecentEpisodesCount,
                contextPackPreview,
                contextPackLoading,
                contextPackError,
                onPreviewContextPack: handlePreviewContextPack,
              }}
            />
          </OperatorPanel>

          <OperatorPanel>
            <OperatorSectionHeader
              title={t("stories.detail.episodeStatusTitle", "Episode production status")}
              action={
                <span className="text-xs text-gray-500">
                  {loadingScripts
                    ? t("stories.detail.scriptsLoading", "Scripts loading")
                    : t("stories.detail.episodeCount", "{count} episodes total").replace("{count}", String(episodes.length))}
                </span>
              }
            />
            <div className="overflow-x-auto">
              <table className={`${operatorTableClass} min-w-[760px]`}>
                <thead className={operatorTableHeadClass}>
                  <tr>
                    <th className="px-5 py-3 text-left font-medium">{t("stories.detail.table.episode", "Episode")}</th>
                    <th className="px-4 py-3 text-left font-medium">{t("common.title", "Title")}</th>
                    <th className="px-4 py-3 text-left font-medium">{t("common.script", "Script")}</th>
                    <th className="px-4 py-3 text-left font-medium">{t("common.timeline", "Timeline")}</th>
                    <th className="px-4 py-3 text-left font-medium">{t("common.storyboard", "Storyboard")}</th>
                    <th className="px-5 py-3 text-right font-medium">{t("common.actions", "Actions")}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {episodes.map((episode) => {
                    const script = latestScript(
                      scriptsByEpisode[episode.id] || [],
                    );
                    const timelineReady = hasTimeline(
                      episode,
                      script,
                      timelinesByEpisode[episode.id] || [],
                    );
                    const storyboardReady = hasStoryboard(script);
                    return (
                      <tr key={episode.id} className={operatorTableRowClass}>
                        <td className="px-5 py-4 font-medium">
                          {t("common.episodeWithNumber", "Episode {number}").replace("{number}", String(episode.episode_number))}
                        </td>
                        <td className="px-4 py-4">{episode.title}</td>
                        <ReadyCell ready={Boolean(script)} />
                        <ReadyCell ready={timelineReady} />
                        <ReadyCell ready={storyboardReady} />
                        <td className="px-5 py-4 text-right">
                          <Link
                            href={episodeWorkspaceHref(
                              episode.business_id || episode.id,
                              { tab: "timeline", scriptId: script?.id },
                            )}
                            className={operatorButtonClass(
                              "primary",
                              "whitespace-nowrap",
                            )}
                          >
                            {t("common.openTimeline", "Open timeline")}
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </OperatorPanel>
        </OperatorMainCanvas>
      }
      inspector={
        <OperatorInspector title={t("stories.detail.productionControl", "Production control")} subtitle={t("stories.detail.productionControlSubtitle", "Readiness checks and production preparation")}>
          <h2 className="text-sm font-semibold">{t("stories.detail.ipProductionPrep", "IP production readiness")}</h2>
          <div className="mt-4">
            <StoryReadinessPanel
              readiness={readiness}
              loading={readinessLoading}
              error={readinessError}
              quickFixLoading={quickFixLoading}
              onRefreshReadiness={checkReadiness}
              onQuickFix={runQuickFix}
            />
          </div>
        </OperatorInspector>
      }
    />
  );
}
