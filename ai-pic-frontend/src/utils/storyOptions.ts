import type { StoryGenerationRequest } from "@/utils/api/types";

export const STORY_GENRES = [
  { value: "drama", label: "Drama" },
  { value: "comedy", label: "Comedy" },
  { value: "romance", label: "Romance" },
  { value: "thriller", label: "Thriller" },
  { value: "action", label: "Action" },
  { value: "fantasy", label: "Fantasy" },
  { value: "sci-fi", label: "Sci-Fi" },
  { value: "horror", label: "Horror" },
  { value: "mystery", label: "Mystery" },
  { value: "historical", label: "Historical" },
];

export const STORY_STATUSES = [
  { value: "", label: "All statuses" },
  { value: "draft", label: "Draft" },
  { value: "approved", label: "Approved" },
  { value: "published", label: "Published" },
];

export type StoryFormat = "short_drama" | "tv_series" | "film";

export const STORY_FORMATS: Array<{ value: StoryFormat; label: string }> = [
  { value: "short_drama", label: "Short drama" },
  { value: "tv_series", label: "TV series / web series" },
  { value: "film", label: "Film" },
];

export type StoryAspectRatio = "9:16" | "16:9";

export const STORY_ASPECT_RATIOS: Array<{
  value: StoryAspectRatio;
  label: string;
}> = [
  { value: "9:16", label: "9:16 Vertical" },
  { value: "16:9", label: "16:9 Horizontal" },
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
