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
    label: "Betrayal at the Engagement Banquet · Revenge Counterattack",
    description:
      "Open with a humiliating betrayal -> turn the tables with evidence in the middle -> end on a bigger conspiracy cliffhanger; ideal for workplace or wealthy-family revenge arcs.",
    defaults: {
      genre: "drama",
      market_region: "SEA",
      micro_genre: "Wealthy family intrigue / workplace revenge",
      pacing_template: "twist-heavy",
      theme: "Betrayal and revenge, identity reversals, righteous payback",
      target_audience: "Female-focused wish-fulfillment drama audience",
      duration_minutes: 30,
      setting_time: "Modern day",
      setting_location: "Tier-one city / international metropolis",
      world_building:
        "Interwoven wealthy-family and workplace power struggles: engagement banquet, company projects, and undercurrents of capital; the evidence trail and identity threads run throughout.",
      additional_requirements:
        "Required: every episode must include one filmable payoff moment (humiliation reversal, counterattack, reveal, punishment, turnaround, rescue, or confession) plus an escalated ending cliffhanger; keep each episode to 3-6 scenes and prioritize reusing major locations; dialogue should be brief, high-density, and free of filler.",
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
    label: "Hit Structure (HOOK → ESCALATION → PAYOFF → CLIFFHANGER)",
    description:
      "Forces an opening hook, a clear payoff beat, and an ending cliffhanger, and requires HOOK/PAYOFF/CLIFFHANGER tags in scenes.notes.",
    defaults: {
      dialogue_style: "natural",
      scene_detail_level: "medium",
      additional_requirements:
        "Output the script using a hit short-drama structure: the first 10 seconds must contain a major hook (HOOK), the middle section must escalate quickly, the final section must include one clear and filmable payoff event (PAYOFF), and the last scene must leave a bigger suspense beat or heightened crisis (CLIFFHANGER). Explicitly tag HOOK/PAYOFF/CLIFFHANGER in scenes[].notes. Dialogue must be short, information-dense, and packed with action and emotion. Avoid filler and do not use “...” to skip lines.",
    },
  },
];
