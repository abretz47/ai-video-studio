"use client";

import { useCallback, useState } from "react";

import { episodeAPI } from "@/utils/api/endpoints";
import { httpClient } from "@/utils/api/client";
import type { EpisodeGenerationRequest } from "@/utils/api/types";
import { useToast } from "@/components/shared/notifications";
import { useGenerationTaskTracker } from "@/hooks/useGenerationTaskTracker";
import { INITIAL_EPISODE_GEN_FORM } from "@/hooks/storyEpisodeGenerationForm";
import type { EpisodeGenForm } from "@/hooks/storyEpisodeGenerationForm";

interface UseStoryEpisodeGenerationOptions {
  storyId: number | null;
  showAlert: (options: {
    message: string;
    variant: "success" | "error" | "warning" | "info";
  }) => void;
  onRefreshAfterSync: () => Promise<void>;
}

export function useStoryEpisodeGeneration({
  storyId,
  showAlert,
  onRefreshAfterSync,
}: UseStoryEpisodeGenerationOptions) {
  const [genOpen, setGenOpen] = useState(false);
  const [genForm, setGenForm] = useState<EpisodeGenForm>(
    INITIAL_EPISODE_GEN_FORM,
  );
  const [promptPreview, setPromptPreview] = useState("");
  const [useAsync, setUseAsync] = useState(true);
  const { notify } = useToast();
  const episodesTracker = useGenerationTaskTracker<"episodes">({
    labels: { episodes: "Episodes" },
    onCompleted: () => onRefreshAfterSync(),
    onNotify: notify,
  });

  // Context Pack preview + toggles (for debugging/context transparency).
  const [contextPackPreview, setContextPackPreview] = useState("");
  const [contextPackLoading, setContextPackLoading] = useState(false);
  const [contextPackError, setContextPackError] = useState("");
  const [includeContinuityLedger, setIncludeContinuityLedger] = useState(true);
  const [includeCharacterCards, setIncludeCharacterCards] = useState(true);
  const [recentEpisodesCount, setRecentEpisodesCount] = useState(3);

  const buildEpisodePayload = useCallback(
    (): EpisodeGenerationRequest => ({
      story_id: storyId ?? 0,
      episode_count: genForm.episode_count,
      episode_duration: genForm.episode_duration,
      market_region: genForm.market_region || undefined,
      micro_genre: genForm.micro_genre || undefined,
      hook_plan: genForm.hook_plan,
      twist_density: genForm.twist_density || undefined,
      cliffhanger_plan: genForm.cliffhanger_plan.length
        ? genForm.cliffhanger_plan
        : undefined,
      ad_snippets: genForm.ad_snippets.length ? genForm.ad_snippets : undefined,
      pacing_template: genForm.pacing_template || undefined,
      plot_complexity: genForm.plot_complexity,
      pacing: genForm.pacing,
      additional_requirements: genForm.additional_requirements || undefined,
      style_preferences: genForm.style_preferences.length
        ? genForm.style_preferences
        : undefined,
      model: genForm.model || undefined,
      temperature: genForm.temperature,
    }),
    [genForm, storyId],
  );

  const handlePreviewPrompt = useCallback(async () => {
    setPromptPreview("Loading...");
    const payload = buildEpisodePayload();
    const res = await episodeAPI.previewEpisodePrompt(payload);
    if (res.success && res.data) {
      setPromptPreview(res.data.prompt ?? "(No content)");
    } else {
      setPromptPreview("Failed to generate prompt");
    }
  }, [buildEpisodePayload]);

  const handlePreviewContextPack = useCallback(async () => {
    setContextPackLoading(true);
    setContextPackError("");
    try {
      const payload = buildEpisodePayload();
      const body = {
        ...payload,
        budget: {
          max_recent_episode_summaries: Math.max(
            0,
            Math.min(50, recentEpisodesCount),
          ),
        },
        include_continuity_ledger: includeContinuityLedger,
        include_character_cards: includeCharacterCards,
        include_recent_episodes: recentEpisodesCount > 0,
      };
      const res = await httpClient<unknown>(
        "/api/v1/episodes/context-pack/preview",
        {
          method: "POST",
          body: JSON.stringify(body),
        },
      );
      if (res.success && res.data) {
        setContextPackPreview(JSON.stringify(res.data, null, 2));
      } else {
        setContextPackPreview("");
        setContextPackError(res.error || "Context preview failed");
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setContextPackPreview("");
      setContextPackError(message || "Context preview failed");
    } finally {
      setContextPackLoading(false);
    }
  }, [
    buildEpisodePayload,
    includeCharacterCards,
    includeContinuityLedger,
    recentEpisodesCount,
  ]);

  const handleGenerateEpisodes = useCallback(async () => {
    const payload = buildEpisodePayload();
    if (useAsync) {
      const response = await episodeAPI.generateEpisodesAsync(payload);
      if (response.success && response.data) {
        notify(
          `Episode generation task submitted #${response.data.task_id}. The list will refresh automatically when it finishes.`,
          "info",
        );
        episodesTracker.track("episodes", response.data.task_id);
      } else {
        showAlert({
          message: `Generation failed: ${response.error || "Unknown error"}`,
          variant: "error",
        });
      }
      return;
    }

    const response = await episodeAPI.generateEpisodes(payload);
    if (response.success) {
      await onRefreshAfterSync();
      showAlert({ message: "Generated successfully", variant: "success" });
    } else {
      showAlert({
        message: `Generation failed: ${response.error || "Unknown error"}`,
        variant: "error",
      });
    }
  }, [
    buildEpisodePayload,
    episodesTracker,
    notify,
    onRefreshAfterSync,
    showAlert,
    useAsync,
  ]);

  return {
    episodesTask: episodesTracker.tasks.episodes ?? null,
    genOpen,
    setGenOpen,
    genForm,
    setGenForm,
    promptPreview,
    useAsync,
    setUseAsync,
    handlePreviewPrompt,
    handleGenerateEpisodes,

    contextPackPreview,
    contextPackLoading,
    contextPackError,
    includeContinuityLedger,
    setIncludeContinuityLedger,
    includeCharacterCards,
    setIncludeCharacterCards,
    recentEpisodesCount,
    setRecentEpisodesCount,
    handlePreviewContextPack,
  };
}
