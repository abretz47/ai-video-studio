export type TaskTypeOption = { value: string; label: string };

export const TASK_TYPE_OPTIONS: TaskTypeOption[] = [
  { value: "", label: "All Types" },
  { value: "story_generation", label: "Story Generation" },
  { value: "episode_generation", label: "Episode Generation" },
  { value: "script_generation", label: "Script Generation" },
  { value: "script_review", label: "Script Review" },
  { value: "dialogue_audio_generation", label: "Dialogue Audio Generation" },
  { value: "timeline_generation", label: "Timeline Generation" },
  { value: "timeline_pipeline", label: "One-Click Timeline Pipeline" },
  { value: "storyboard_generation", label: "Storyboard Generation" },
  { value: "storyboard_image_generation", label: "Storyboard Image Generation" },
  { value: "video_generation", label: "Video Generation" },
  { value: "virtual_ip_image_generation", label: "Virtual IP Text-to-Image" },
  { value: "virtual_ip_image_variant_generation", label: "Virtual IP Image-to-Image" },
  { value: "environment_image_generation", label: "Environment Text-to-Image" },
  { value: "environment_image_variant_generation", label: "Environment Image-to-Image" },
  { value: "image_generation", label: "Image Generation" },
  { value: "image_edit", label: "Image Editing" },
  { value: "image_enhancement", label: "Image Enhancement" },
  { value: "text_generation", label: "Text Generation" },
];

export const TASK_TYPE_LABELS = Object.fromEntries(
  TASK_TYPE_OPTIONS.filter((opt) => opt.value).map((opt) => [
    opt.value,
    opt.label,
  ]),
) as Record<string, string>;
