import { t } from "@/lib/i18n";
import type { StoryGenerationRequest } from "@/utils/api/types";

export const STORY_GENRES = [
  { value: "drama", label: t("storyOptions.genre.drama", "Drama") },
  { value: "comedy", label: t("storyOptions.genre.comedy", "Comedy") },
  { value: "romance", label: t("storyOptions.genre.romance", "Romance") },
  { value: "thriller", label: t("storyOptions.genre.thriller", "Thriller") },
  { value: "action", label: t("storyOptions.genre.action", "Action") },
  { value: "fantasy", label: t("storyOptions.genre.fantasy", "Fantasy") },
  { value: "sci-fi", label: t("storyOptions.genre.scifi", "Sci-Fi") },
  { value: "horror", label: t("storyOptions.genre.horror", "Horror") },
  { value: "mystery", label: t("storyOptions.genre.mystery", "Mystery") },
  { value: "historical", label: t("storyOptions.genre.historical", "Historical") },
];

export const STORY_STATUSES = [
  { value: "", label: t("storyOptions.status.all", "All statuses") },
  { value: "draft", label: t("storyOptions.status.draft", "Draft") },
  { value: "approved", label: t("storyOptions.status.approved", "Approved") },
  { value: "published", label: t("storyOptions.status.published", "Published") },
];

export type StoryFormat = "short_drama" | "tv_series" | "film";

export const STORY_FORMATS: Array<{ value: StoryFormat; label: string }> = [
  { value: "short_drama", label: t("storyOptions.format.shortDrama", "Short drama") },
  { value: "tv_series", label: t("storyOptions.format.tvSeries", "TV / web series") },
  { value: "film", label: t("storyOptions.format.film", "Film") },
];

export type StoryAspectRatio = "9:16" | "16:9";

export const STORY_ASPECT_RATIOS: Array<{
  value: StoryAspectRatio;
  label: string;
}> = [
  { value: "9:16", label: t("storyOptions.aspectRatio.vertical", "9:16 Vertical") },
  { value: "16:9", label: t("storyOptions.aspectRatio.horizontal", "16:9 Horizontal") },
];

export type StoryGenerationForm = StoryGenerationRequest & {
  story_format: StoryFormat;
};

export const STORY_GENERATE_DEFAULTS: StoryGenerationForm = {
  title: "",
  story_format: "short_drama",
  genre: "drama",
  market_region: "",
  micro_genre: "",
  pacing_template: "",
  theme: "",
  target_audience: "",
  duration_minutes: 30,
  default_aspect_ratio: "9:16",
  character_ids: [],
  setting_time: "",
  setting_location: "",
  world_building: "",
  additional_requirements: "",
  style_preferences: [],
  content_restrictions: [],
  tags: [],
  model: "",
  temperature: 0.7,
};
