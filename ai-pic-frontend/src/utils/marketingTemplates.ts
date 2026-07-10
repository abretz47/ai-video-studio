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
  { value: "NA", label: "North America", description: "Revenge arcs, werewolves, and mafia skins perform more smoothly" },
  { value: "LATAM", label: "Latin America", description: "Family conflicts and emotional push-pull are widely accepted" },
  {
    value: "SEA",
    label: "Southeast Asia",
    description: "CEO romance, contract marriage, and campus relationship stories perform reliably",
  },
  { value: "MENA", label: "Middle East", description: "Family power struggles and inheritance arcs are a safer fit" },
  { value: "KRJP", label: "Korea/Japan", description: "Idol, campus, and workplace romance convert more easily" },
  { value: "GLOBAL", label: "Global", description: "A conservative template that is easy to reuse across regions" },
];

export const MICRO_GENRES = [
  { value: "mafia-revenge", label: "Mafia revenge" },
  { value: "werewolf-mate", label: "Werewolf / fated mate" },
  { value: "billionaire-identity", label: "CEO / hidden identity" },
  { value: "secret-baby", label: "Secret child / heir" },
  { value: "contract-marriage", label: "Contract marriage" },
  { value: "campus-revenge", label: "Campus comeback" },
  { value: "idol-scandal", label: "Idol scandal romance" },
  { value: "family-intrigue", label: "Wealthy family intrigue" },
];

export const PACING_TEMPLATES: PacingTemplate[] = [
  {
    id: "fast-hook",
    label: "Fast Hook Sprint",
    description:
      "Deliver a major beat within the first 5 seconds, land the first reversal within 30 seconds, and end with a clear cliffhanger that locks in the next episode.",
    hookPlan: {
      opening_hook: "Use a single line or action to ignite the conflict within 5 seconds.",
      escalation_plan: "Intensify the humiliation or betrayal emotion quickly between 20-40 seconds.",
      payoff_plan: "Use the final 2-3 seconds for a decisive counterattack or identity reversal.",
      key_reversals: [
        {
          beat_type: "reversal",
          description: "An identity or stance reversal that drives the revenge momentum",
          timing: "Middle",
          intensity: "high",
        },
      ],
    },
    twistDensity: "1-2 per episode",
    cliffhangerPlan: ["Reveal a key identity or threat in the final 3 seconds"],
    adSnippets: [
      {
        duration_seconds: 15,
        hook: "Humiliated at the opening -> powerful counterattack",
        visual_summary: "Close-up expression shot + a sharp comeback moment",
        call_to_action: "Want to see how she turns it around? Keep watching",
      },
      {
        duration_seconds: 30,
        hook: "Identity reversal + escalating conflict",
        visual_summary: "A power entrance + the opponent falling apart",
        call_to_action: "The next episode reveals the truth",
      },
    ],
  },
  {
    id: "twist-heavy",
    label: "Twist-Heavy",
    description: "At least two reversals per episode, with fast emotional swings and reaction shots that speed up the payoff.",
    hookPlan: {
      opening_hook: "Open with the conflict outcome or a striking payoff image.",
      escalation_plan: "Insert a reversal, misunderstanding, or exposure every 20 seconds.",
      payoff_plan: "Use a second reversal near the end to create shock.",
      key_reversals: [
        {
          beat_type: "hook",
          description: "Show an irreversible conflict outcome right at the opening",
          timing: "Opening",
          intensity: "high",
        },
        {
          beat_type: "reversal",
          description: "A double reversal in the middle section",
          timing: "Middle",
          intensity: "high",
        },
      ],
    },
    twistDensity: "2+ per episode",
    cliffhangerPlan: ["Use an unrevealed secret as the next episode hook"],
    adSnippets: [
      {
        duration_seconds: 15,
        hook: "Rapid-fire twists that leave viewers stunned",
        visual_summary: "Expression changes + fast cut transitions",
        call_to_action: "Don't blink—the twists aren't over yet",
      },
      {
        duration_seconds: 60,
        hook: "A chain of multiple reversals",
        visual_summary: "Fast-paced editing across multiple scenes",
        call_to_action: "Unlock the next part of the story now",
      },
    ],
  },
  {
    id: "slow-burn",
    label: "Emotional Build",
    description: "Plant early setup, build emotional pressure, and release it in a concentrated burst around 60-80 seconds; ideal for relationship-driven arcs.",
    hookPlan: {
      opening_hook: "Establish the key relationship and its taboo at the start.",
      escalation_plan: "Gradually deepen the misunderstanding and emotional pressure.",
      payoff_plan: "End with an emotional release or a key decision.",
      key_reversals: [
        {
          beat_type: "payoff",
          description: "Emotional release or confession",
          timing: "Ending",
          intensity: "medium",
        },
      ],
    },
    twistDensity: "1 per episode",
    cliffhangerPlan: ["Use an emotional choice as the cliffhanger"],
    adSnippets: [
      {
        duration_seconds: 30,
        hook: "Emotional restraint -> finally breaking down",
        visual_summary: "Locked eye contact, turning away, tears",
        call_to_action: "The ending is about to be revealed",
      },
    ],
  },
];
