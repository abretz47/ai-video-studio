import { t } from "@/lib/i18n";

export type ScriptTabId = "overview" | "scenes" | "traffic";

export const SCRIPT_TABS: Array<{
  id: ScriptTabId;
  name: string;
  description: string;
}> = [
  {
    id: "overview",
    name: t("script.tabs.overview", "Overview"),
    description: t("script.tabs.overviewDescription", "Script text and metrics"),
  },
  {
    id: "scenes",
    name: t("script.tabs.scenes", "Scenes"),
    description: t("script.tabs.scenesDescription", "Review dialogue and directions by scene"),
  },
  {
    id: "traffic",
    name: t("script.tabs.traffic", "Traffic / Score"),
    description: t("script.tabs.trafficDescription", "Hook scores and creative assets"),
  },
];
