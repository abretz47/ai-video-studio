import { t } from "@/lib/i18n";

type HookBeat = {
  beat_type?: string;
  description: string;
  timing?: string;
  intensity?: string;
};

type HookPlan = {
  opening_hook?: string;
  escalation_plan?: string;
  payoff_plan?: string;
  key_reversals?: HookBeat[];
};

type AdSnippet = {
  duration_seconds?: number;
  hook: string;
  visual_summary?: string;
  call_to_action?: string;
};

export type PacingTemplate = {
  id: string;
  label: string;
  description: string;
  hookPlan: HookPlan;
  twistDensity?: string;
  cliffhangerPlan?: string[];
  adSnippets?: AdSnippet[];
};

export const MARKET_REGIONS = [
  {
    value: "NA",
    label: t("marketing.region.na", "North America"),
    description: t(
      "marketing.region.naDescription",
      "Revenge arcs, werewolves, and mafia skins convert more smoothly.",
    ),
  },
  {
    value: "LATAM",
    label: t("marketing.region.latam", "Latin America"),
    description: t(
      "marketing.region.latamDescription",
      "Family conflict and emotional push-pull resonate well.",
    ),
  },
  {
    value: "SEA",
    label: t("marketing.region.sea", "Southeast Asia"),
    description: t(
      "marketing.region.seaDescription",
      "CEO romance, contract marriage, and school emotion beats perform consistently.",
    ),
  },
  {
    value: "MENA",
    label: t("marketing.region.mena", "Middle East"),
    description: t(
      "marketing.region.menaDescription",
      "Family power struggles and inheritance lines are safer bets.",
    ),
  },
  {
    value: "KRJP",
    label: t("marketing.region.krjp", "Korea / Japan"),
    description: t(
      "marketing.region.krjpDescription",
      "Idol, school, and workplace romance tends to convert better.",
    ),
  },
  {
    value: "GLOBAL",
    label: t("marketing.region.global", "Global"),
    description: t(
      "marketing.region.globalDescription",
      "Conservative template that is easier to reuse across regions.",
    ),
  },
];

export const MICRO_GENRES = [
  { value: "mafia-revenge", label: t("marketing.microGenre.mafiaRevenge", "Mafia revenge") },
  { value: "werewolf-mate", label: t("marketing.microGenre.werewolfMate", "Werewolf / fated mate") },
  { value: "billionaire-identity", label: t("marketing.microGenre.billionaireIdentity", "Billionaire / hidden identity") },
  { value: "secret-baby", label: t("marketing.microGenre.secretBaby", "Secret baby / heir") },
  { value: "contract-marriage", label: t("marketing.microGenre.contractMarriage", "Contract marriage") },
  { value: "campus-revenge", label: t("marketing.microGenre.campusRevenge", "Campus comeback") },
  { value: "idol-scandal", label: t("marketing.microGenre.idolScandal", "Idol scandal romance") },
  { value: "family-intrigue", label: t("marketing.microGenre.familyIntrigue", "Power family intrigue") },
];

export const PACING_TEMPLATES: PacingTemplate[] = [
  {
    id: "fast-hook",
    label: t("marketing.pacing.fastHook.label", "Fast hook sprint"),
    description: t(
      "marketing.pacing.fastHook.description",
      "Explode within 5 seconds, land the first twist inside 30 seconds, and lock the next episode with a clear cliffhanger.",
    ),
    hookPlan: {
      opening_hook: t("marketing.pacing.fastHook.openingHook", "Use one line or action to ignite conflict within 5 seconds."),
      escalation_plan: t("marketing.pacing.fastHook.escalationPlan", "Raise humiliation or betrayal emotions quickly in 20-40 seconds."),
      payoff_plan: t("marketing.pacing.fastHook.payoffPlan", "Use the last 2-3 seconds for a clear counterattack or identity reversal."),
      key_reversals: [
        {
          beat_type: "reversal",
          description: t("marketing.pacing.fastHook.reversalDescription", "Reverse identity or stance to drive the revenge beat."),
          timing: t("marketing.common.midSection", "Mid-section"),
          intensity: "high",
        },
      ],
    },
    twistDensity: t("marketing.pacing.fastHook.twistDensity", "1-2 / episode"),
    cliffhangerPlan: [t("marketing.pacing.fastHook.cliffhanger", "Reveal the key identity or threat in the final 3 seconds.")],
    adSnippets: [
      {
        duration_seconds: 15,
        hook: t("marketing.pacing.fastHook.ad1.hook", "Humiliated at the opening -> instant payback"),
        visual_summary: t("marketing.pacing.fastHook.ad1.visual", "Close-up emotion + slap-back shot"),
        call_to_action: t("marketing.pacing.fastHook.ad1.cta", "Want to see her flip the game? Keep watching."),
      },
      {
        duration_seconds: 30,
        hook: t("marketing.pacing.fastHook.ad2.hook", "Identity reversal + conflict escalation"),
        visual_summary: t("marketing.pacing.fastHook.ad2.visual", "Power entrance + rival breakdown"),
        call_to_action: t("marketing.pacing.fastHook.ad2.cta", "The next episode reveals the truth."),
      },
    ],
  },
  {
    id: "twist-heavy",
    label: t("marketing.pacing.twistHeavy.label", "High-density twists"),
    description: t(
      "marketing.pacing.twistHeavy.description",
      "At least two twists per episode with rapid emotional swings and reaction shots that accelerate payoff release.",
    ),
    hookPlan: {
      opening_hook: t("marketing.pacing.twistHeavy.openingHook", "Open with the result of the conflict or an explosive image."),
      escalation_plan: t("marketing.pacing.twistHeavy.escalationPlan", "Insert a twist, misunderstanding, or exposure every 20 seconds."),
      payoff_plan: t("marketing.pacing.twistHeavy.payoffPlan", "End with a second reversal that creates shock."),
      key_reversals: [
        {
          beat_type: "hook",
          description: t("marketing.pacing.twistHeavy.hookDescription", "Start with an irreversible conflict result."),
          timing: t("marketing.common.opening", "Opening"),
          intensity: "high",
        },
        {
          beat_type: "reversal",
          description: t("marketing.pacing.twistHeavy.reversalDescription", "Double reversal in the middle section."),
          timing: t("marketing.common.midSection", "Mid-section"),
          intensity: "high",
        },
      ],
    },
    twistDensity: t("marketing.pacing.twistHeavy.twistDensity", "2+ / episode"),
    cliffhangerPlan: [t("marketing.pacing.twistHeavy.cliffhanger", "Use an unrevealed secret as the next-episode hook.")],
    adSnippets: [
      {
        duration_seconds: 15,
        hook: t("marketing.pacing.twistHeavy.ad1.hook", "Rapid twists that keep viewers stunned"),
        visual_summary: t("marketing.pacing.twistHeavy.ad1.visual", "Reaction cuts + fast edit switches"),
        call_to_action: t("marketing.pacing.twistHeavy.ad1.cta", "Don’t blink, the twists are not over."),
      },
      {
        duration_seconds: 60,
        hook: t("marketing.pacing.twistHeavy.ad2.hook", "A chain of twists stacked back to back"),
        visual_summary: t("marketing.pacing.twistHeavy.ad2.visual", "Rapid multi-scene montage"),
        call_to_action: t("marketing.pacing.twistHeavy.ad2.cta", "Unlock the next plot turn now."),
      },
    ],
  },
  {
    id: "slow-burn",
    label: t("marketing.pacing.slowBurn.label", "Emotional escalation"),
    description: t(
      "marketing.pacing.slowBurn.description",
      "Plant early foreshadowing, compress pressure, and release emotion around 60-80 seconds—great for relationship arcs.",
    ),
    hookPlan: {
      opening_hook: t("marketing.pacing.slowBurn.openingHook", "Open by naming the key relationship and taboo."),
      escalation_plan: t("marketing.pacing.slowBurn.escalationPlan", "Deepen the misunderstanding and emotional pressure step by step."),
      payoff_plan: t("marketing.pacing.slowBurn.payoffPlan", "Close on an emotional release or decisive choice."),
      key_reversals: [
        {
          beat_type: "payoff",
          description: t("marketing.pacing.slowBurn.payoffDescription", "Emotional release / confession"),
          timing: t("marketing.common.ending", "Ending"),
          intensity: "medium",
        },
      ],
    },
    twistDensity: t("marketing.pacing.slowBurn.twistDensity", "1 / episode"),
    cliffhangerPlan: [t("marketing.pacing.slowBurn.cliffhanger", "Use an emotional choice as the episode hook.")],
    adSnippets: [
      {
        duration_seconds: 30,
        hook: t("marketing.pacing.slowBurn.ad1.hook", "Emotion builds -> finally explodes"),
        visual_summary: t("marketing.pacing.slowBurn.ad1.visual", "Eye contact, turning away, tear beat"),
        call_to_action: t("marketing.pacing.slowBurn.ad1.cta", "The ending is about to be revealed."),
      },
    ],
  },
];
