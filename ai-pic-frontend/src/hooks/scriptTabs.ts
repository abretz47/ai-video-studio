export type ScriptTabId = "overview" | "scenes" | "traffic";

export const SCRIPT_TABS: Array<{
  id: ScriptTabId;
  name: string;
  description: string;
}> = [
  { id: "overview", name: "Overview", description: "Script text and stats" },
  { id: "scenes", name: "Scenes", description: "View dialogue and instructions by scene" },
  { id: "traffic", name: "Promotion / Rating", description: "Highlight score and asset checklist" },
];
