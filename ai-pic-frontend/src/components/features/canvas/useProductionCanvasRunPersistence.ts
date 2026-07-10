import { t } from "@/lib/i18n";
import { useCallback, useEffect, useRef, useState } from "react";
import { productionCanvasAPI } from "@/utils/api/endpoints";
import {
  canvasRunIdFromNodes,
  productionCanvasStateFromRun,
  toProductionCanvasSavedState,
} from "./productionCanvasPersistence";
import type { ProductionCanvasState } from "./productionCanvasState";

export function useProductionCanvasRunPersistence({
  autosaveDelayMs = 1200,
  canvasState,
  replaceCanvasState,
}: {
  autosaveDelayMs?: number | null;
  canvasState: ProductionCanvasState;
  replaceCanvasState: (state: ProductionCanvasState) => void;
}) {
  const [runId, setRunId] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const lastSavedSignature = useRef("");
  const autosaveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const resolvedRunId = useCallback(
    (state: ProductionCanvasState = canvasState) =>
      runId.trim() || canvasRunIdFromNodes(state.nodes),
    [canvasState, runId],
  );

  const stateSignature = useCallback(
    (targetRunId: string, state: ProductionCanvasState) =>
      JSON.stringify({
        runId: targetRunId,
        state: toProductionCanvasSavedState(state),
      }),
    [],
  );

  const saveCanvasState = useCallback(
    async (
      targetRunId: string,
      state: ProductionCanvasState,
      mode: "manual" | "auto",
    ) => {
      if (busy) {
        setStatus(t("canvas.persistence.saving", "Saving"));
        return;
      }
      const signature = stateSignature(targetRunId, state);
      if (mode === "auto" && signature === lastSavedSignature.current) return;
      setBusy(true);
      setStatus(mode === "auto" ? t("canvas.persistence.autoSaving", "Auto-saving") : t("canvas.persistence.saving", "Saving"));
      try {
        const savedState = toProductionCanvasSavedState(state);
        const response = await productionCanvasAPI.saveRunState(
          targetRunId,
          savedState,
        );
        if (!response.success || !response.data) {
          setStatus(response.error || t("canvas.persistence.saveFailed", "Save failed"));
          return;
        }
        const nextRunId = response.data.run_id || targetRunId;
        lastSavedSignature.current = stateSignature(nextRunId, state);
        setRunId(nextRunId);
        setStatus(mode === "auto" ? t("canvas.persistence.autoSaved", "Auto-saved") : t("canvas.persistence.saved", "Saved"));
      } catch (err) {
        setStatus(err instanceof Error ? err.message : String(err));
      } finally {
        setBusy(false);
      }
    },
    [busy, stateSignature],
  );

  const saveCanvas = async () => {
    const targetRunId = resolvedRunId();
    if (!targetRunId) {
      setStatus(t("canvas.persistence.missingRunId", "Missing Run ID"));
      return;
    }
    await saveCanvasState(targetRunId, canvasState, "manual");
  };

  useEffect(() => {
    if (autosaveDelayMs === null || autosaveDelayMs < 0 || busy) return;
    const targetRunId = resolvedRunId();
    if (!targetRunId) return;
    const signature = stateSignature(targetRunId, canvasState);
    if (signature === lastSavedSignature.current) return;
    autosaveTimer.current = setTimeout(() => {
      void saveCanvasState(targetRunId, canvasState, "auto");
    }, autosaveDelayMs);
    return () => {
      if (autosaveTimer.current) clearTimeout(autosaveTimer.current);
    };
  }, [
    autosaveDelayMs,
    busy,
    canvasState,
    resolvedRunId,
    saveCanvasState,
    stateSignature,
  ]);

  const restoreCanvas = async () => {
    const targetRunId = resolvedRunId();
    if (!targetRunId || busy) {
      setStatus(t("canvas.persistence.missingRunId", "Missing Run ID"));
      return;
    }
    setBusy(true);
    setStatus(t("canvas.persistence.restoring", "Restoring"));
    try {
      const response = await productionCanvasAPI.getRun(targetRunId);
      if (!response.success || !response.data) {
        setStatus(response.error || t("canvas.persistence.restoreFailed", "Restore failed"));
        return;
      }
      const restoredState = productionCanvasStateFromRun(response.data);
      const nextRunId = response.data.run_id || targetRunId;
      replaceCanvasState(restoredState);
      lastSavedSignature.current = stateSignature(nextRunId, restoredState);
      setRunId(nextRunId);
      setStatus(t("canvas.persistence.restored", "Restored"));
    } catch (err) {
      setStatus(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  return {
    busy,
    restoreCanvas,
    runId,
    saveCanvas,
    setRunId,
    status,
  };
}
