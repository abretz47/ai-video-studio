export type ProductionCanvasNodeKind = "pipeline" | "note" | "skill_result";

export type ProductionCanvasReuseTarget = {
  kind: "api" | "repository" | "service" | "worker" | "artifact";
  label: string;
  target: string;
  description?: string | null;
};

export type ProductionCanvasEdge = {
  from: string;
  to: string;
};

export type ProductionCanvasNode = {
  id: string;
  label: string;
  title: string;
  status: "ready" | "running" | "review" | "blocked";
  x: number;
  y: number;
  width: number;
  height?: number;
  kind?: ProductionCanvasNodeKind;
  skill?: string;
  detail?: string;
  outputs?: Record<string, unknown>;
  reuseTargets?: ProductionCanvasReuseTarget[];
  actionHref?: string;
  actionLabel?: string;
};

export const productionCanvasNodes: ProductionCanvasNode[] = [
  {
    id: "brief",
    label: "Brief",
    title: "IP, audience, genre, and episode goal",
    status: "ready",
    x: 40,
    y: 128,
    width: 170,
    detail: "Refine the IP, audience, genre, and episode goal into executable inputs.",
    actionHref: "/virtual-ip",
    actionLabel: "View IP Projects",
  },
  {
    id: "script",
    label: "Script",
    title: "Short drama beats, dialogue, and quality gates",
    status: "ready",
    x: 270,
    y: 64,
    width: 190,
    detail: "Build on the brief to generate short drama beats, dialogue, conflict, and quality gates.",
    actionHref: "/stories",
    actionLabel: "Go to Story Production",
  },
  {
    id: "storyboard",
    label: "Storyboard",
    title: "Shot list, visual descriptions, and storyboard candidates",
    status: "review",
    x: 520,
    y: 64,
    width: 210,
    detail: "Break the script into a shot list, visual descriptions, and reviewable storyboard candidates.",
    actionHref: "/stories",
    actionLabel: "View Storyboard Flow",
  },
  {
    id: "image",
    label: "Image Candidates",
    title: "Character, environment, and keyframe candidates",
    status: "review",
    x: 520,
    y: 228,
    width: 210,
    detail: "Generate candidate images around characters, environments, and keyframes while preserving failure and selection evidence.",
    actionHref: "/environments",
    actionLabel: "View Environment Assets",
  },
  {
    id: "video",
    label: "Video Candidates",
    title: "Image-to-video, model comparison, and failure retries",
    status: "running",
    x: 760,
    y: 148,
    width: 200,
    detail: "Run image-to-video generation, model comparisons, failure retries, and cost tracking for candidate images.",
    actionHref: "/tasks",
    actionLabel: "View Generation Tasks",
  },
  {
    id: "timeline",
    label: "Timeline",
    title: "Shot order, duration, and playable output",
    status: "blocked",
    x: 1000,
    y: 84,
    width: 170,
    detail: "Place usable video candidates into shot order, duration, and a playable timeline.",
    actionHref: "/tasks",
    actionLabel: "View Timeline Tasks",
  },
  {
    id: "report",
    label: "Report",
    title: "Cost, quality, and provider lineage",
    status: "ready",
    x: 1000,
    y: 260,
    width: 170,
    detail: "Summarize cost, quality, provider lineage, and human decision evidence.",
    actionHref: "/tasks",
    actionLabel: "View Report Tasks",
  },
];

export const productionCanvasEdges: ProductionCanvasEdge[] = [
  { from: "brief", to: "script" },
  { from: "script", to: "storyboard" },
  { from: "script", to: "image" },
  { from: "storyboard", to: "video" },
  { from: "image", to: "video" },
  { from: "video", to: "timeline" },
  { from: "video", to: "report" },
];

export const productionCanvasStatusMeta = {
  ready: { label: "Reusable", tone: "green" },
  running: { label: "Generating", tone: "amber" },
  review: { label: "Pending Selection", tone: "blue" },
  blocked: { label: "Missing", tone: "red" },
} as const;
