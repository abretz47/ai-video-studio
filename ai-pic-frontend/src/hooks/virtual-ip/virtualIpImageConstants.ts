import type { StyleSpec, VirtualIPImage } from "@/utils/api/types";

type StyleSpecKey = keyof StyleSpec;

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");

export const VIRTUAL_IP_STYLE_SPEC_FIELDS: Array<{
  key: StyleSpecKey;
  label: string;
}> = [
  { key: "style_universe", label: "Worldbuilding / Art Style System" },
  { key: "character_proportion", label: "Character Proportions" },
  { key: "character_face_style", label: "Facial Features and Character Style" },
  { key: "line_art_style", label: "Line Art Style" },
  { key: "color_render_style", label: "Color Rendering Style" },
  { key: "lighting_style", label: "Shadows and Lighting" },
  { key: "color_mood", label: "Color Mood" },
];

export function resolveImageUrl(image: VirtualIPImage): string {
  if (image.oss_url) return image.oss_url;
  const fp = image.file_path || "";
  if (!fp) return "";
  if (fp.startsWith("http")) return fp;
  return `${API_BASE}${fp.startsWith("/") ? "" : "/"}${fp}`;
}
