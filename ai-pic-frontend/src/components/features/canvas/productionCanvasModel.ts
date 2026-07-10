import { t } from "@/lib/i18n";

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
    title: t("canvas.node.brief.title", "IP, audience, genre, and single-episode objective"),
    status: "ready",
    x: 40,
    y: 128,
    width: 170,
    detail: t("canvas.node.brief.detail", "Turn the IP, audience, genre, and episode objective into executable input."),
    actionHref: "/virtual-ip",
    actionLabel: t("canvas.node.brief.action", "View IP projects"),
  },
  {
    id: "script",
    label: "Script",
    title: t("canvas.node.script.title", "Short-drama beats, dialogue, and quality gates"),
    status: "ready",
    x: 270,
    y: 64,
    width: 190,
    detail: t("canvas.node.script.detail", "Take the brief and generate beats, dialogue, conflict, and quality gates."),
    actionHref: "/stories",
    actionLabel: t("canvas.node.script.action", "Go to story production"),
  },
  {
    id: "storyboard",
    label: "Storyboard",
    title: t("canvas.node.storyboard.title", "Shot list, visual descriptions, and storyboard candidates"),
    status: "review",
    x: 520,
    y: 64,
    width: 210,
    detail: t("canvas.node.storyboard.detail", "Break the script into a shot list, visual descriptions, and reviewable storyboard candidates."),
    actionHref: "/stories",
    actionLabel: t("canvas.node.storyboard.action", "View storyboard workflow"),
  },
  {
    id: "image",
    label: "Image Candidates",
    title: t("canvas.node.image.title", "Character, environment, and keyframe candidates"),
    status: "review",
    x: 520,
    y: 228,
    width: 210,
    detail: t("canvas.node.image.detail", "Generate candidate images around characters, environments, and keyframes while keeping failure and selection evidence."),
    actionHref: "/environments",
    actionLabel: t("canvas.node.image.action", "View environment assets"),
  },
  {
    id: "video",
    label: "Video Candidates",
    title: t("canvas.node.video.title", "Image-to-video, model comparison, and reruns"),
    status: "running",
    x: 760,
    y: 148,
    width: 200,
    detail: t("canvas.node.video.detail", "Run image-to-video, compare models, rerun failures, and record cost across candidate images."),
    actionHref: "/tasks",
    actionLabel: t("canvas.node.video.action", "View generation tasks"),
  },
  {
    id: "timeline",
    label: "Timeline",
    title: t("canvas.node.timeline.title", "Shot order, duration, and playable output"),
    status: "blocked",
    x: 1000,
    y: 84,
    width: 170,
    detail: t("canvas.node.timeline.detail", "Place usable video candidates into shot order, duration, and a playable timeline."),
    actionHref: "/tasks",
    actionLabel: t("canvas.node.timeline.action", "View timeline tasks"),
  },
  {
    id: "report",
    label: "Report",
    title: t("canvas.node.report.title", "Cost, quality, and provider lineage"),
    status: "ready",
    x: 1000,
    y: 260,
    width: 170,
    detail: t("canvas.node.report.detail", "Summarize cost, quality, provider lineage, and human decision evidence."),
    actionHref: "/tasks",
    actionLabel: t("canvas.node.report.action", "View report tasks"),
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
  ready: { label: t("canvas.status.ready", "Reusable"), tone: "green" },
  running: { label: t("canvas.status.running", "Running"), tone: "amber" },
  review: { label: t("canvas.status.review", "Needs selection"), tone: "blue" },
  blocked: { label: t("canvas.status.blocked", "Needs input"), tone: "red" },
} as const;
