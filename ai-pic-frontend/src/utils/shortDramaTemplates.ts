import { t } from "@/lib/i18n";

export type ShortDramaStoryTemplate = {
  id: string;
  label: string;
  description: string;
  defaults: {
    genre?: string;
    market_region?: string;
    micro_genre?: string;
    pacing_template?: string;
    theme?: string;
    target_audience?: string;
    duration_minutes?: number;
    setting_time?: string;
    setting_location?: string;
    world_building?: string;
    additional_requirements?: string;
  };
};

export const SHORT_DRAMA_STORY_TEMPLATES: ShortDramaStoryTemplate[] = [
  {
    id: "engagement-betrayal-revenge",
    label: t(
      "shortDrama.storyTemplate.engagement.label",
      "Engagement betrayal · revenge comeback",
    ),
    description: t(
      "shortDrama.storyTemplate.engagement.description",
      "Start with public humiliation and betrayal, flip the evidence mid-episode, then end on a larger conspiracy cliffhanger—great for workplace and wealthy-family revenge arcs.",
    ),
    defaults: {
      genre: "drama",
      market_region: "SEA",
      micro_genre: t(
        "shortDrama.storyTemplate.engagement.microGenre",
        "Wealthy family intrigue / workplace revenge",
      ),
      pacing_template: "twist-heavy",
      theme: t(
        "shortDrama.storyTemplate.engagement.theme",
        "Betrayal and revenge, identity reversal, righteous payback",
      ),
      target_audience: t(
        "shortDrama.storyTemplate.engagement.audience",
        "Female-leaning catharsis audience",
      ),
      duration_minutes: 30,
      setting_time: t("shortDrama.storyTemplate.engagement.time", "Modern"),
      setting_location: t(
        "shortDrama.storyTemplate.engagement.location",
        "Tier-one city / international metropolis",
      ),
      world_building: t(
        "shortDrama.storyTemplate.engagement.world",
        "Power in wealthy families and the workplace collides across an engagement banquet, company projects, and capital undercurrents; evidence trails and identity arcs run through the story.",
      ),
      additional_requirements: t(
        "shortDrama.storyTemplate.engagement.requirements",
        "Hard rule: every episode must include one filmable catharsis beat (slap-back, counterattack, exposure, punishment, reversal, rescue, confession) plus an escalated end hook; keep 3-6 scenes per episode, reuse major locations when possible, and keep dialogue sharp and information-dense.",
      ),
    },
  },
];

export type ShortDramaScriptTemplate = {
  id: string;
  label: string;
  description: string;
  defaults: {
    dialogue_style?: string;
    scene_detail_level?: string;
    additional_requirements?: string;
  };
};

export const SHORT_DRAMA_SCRIPT_TEMPLATES: ShortDramaScriptTemplate[] = [
  {
    id: "hit-structure",
    label: t(
      "shortDrama.scriptTemplate.hitStructure.label",
      "Hit structure (HOOK → ESCALATION → PAYOFF → CLIFFHANGER)",
    ),
    description: t(
      "shortDrama.scriptTemplate.hitStructure.description",
      "Forces an opening hook, a catharsis beat, and an ending cliffhanger, and requires scenes.notes to mark HOOK / PAYOFF / CLIFFHANGER.",
    ),
    defaults: {
      dialogue_style: "natural",
      scene_detail_level: "medium",
      additional_requirements: t(
        "shortDrama.scriptTemplate.hitStructure.requirements",
        "Write with a breakout short-drama structure: the first 10 seconds must explode with a hook, the middle must escalate quickly, the ending must contain one clear filmable payoff event, and the final scene must leave a larger suspense or crisis escalation. Mark HOOK / PAYOFF / CLIFFHANGER in scenes[].notes. Keep dialogue short, emotional, physical, and information-dense—avoid filler and ellipses.",
      ),
    },
  },
];
