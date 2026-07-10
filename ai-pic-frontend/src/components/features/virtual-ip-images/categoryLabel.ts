const CATEGORY_LABELS: Record<string, string> = {
  portrait: "Portrait",
  full_body: "Full Body",
  scene: "Scene",
  action: "Action",
  emotion: "Emotion",
};

export const getCategoryLabel = (category: string): string =>
  CATEGORY_LABELS[category] || category;
