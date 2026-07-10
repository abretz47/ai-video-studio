import { useEffect, type Dispatch, type SetStateAction } from "react";

import { scriptAPI } from "@/utils/api/endpoints";
import type { Script } from "@/utils/api/types";
import {
  mergeScriptDetail,
  scriptNeedsDetail,
} from "@/hooks/episode/scriptDetailHydration";

export function useSelectedScriptDetailHydration(
  selectedScript: Script | null,
  setScripts: Dispatch<SetStateAction<Script[]>>,
) {
  useEffect(() => {
    if (!selectedScript || !scriptNeedsDetail(selectedScript)) return;
    let cancelled = false;
    const loadSelectedScriptDetail = async () => {
      try {
        const response = await scriptAPI.getScript(
          selectedScript.business_id || selectedScript.id,
        );
        if (!cancelled && response.success && response.data) {
          setScripts((prev) =>
            mergeScriptDetail(prev, response.data as Script),
          );
        }
      } catch (error) {
        console.error("Failed to load script details:", error);
      }
    };
    void loadSelectedScriptDetail();
    return () => {
      cancelled = true;
    };
  }, [selectedScript, setScripts]);
}
