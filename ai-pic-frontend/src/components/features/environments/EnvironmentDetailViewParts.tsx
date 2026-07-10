import {
  GenerationAuditWarnings,
  OperatorPanel,
  OperatorSectionHeader,
  OperatorState,
  StatusPill,
  operatorButtonClass,
} from "@/components/shared";
import type { Environment } from "@/utils/api/types";

interface EnvironmentDetailActionsProps {
  editing: boolean;
  saving: boolean;
  onEdit: () => void;
  onCancel: () => void;
  onSave: () => void;
}

export function EnvironmentDetailActions({
  editing,
  saving,
  onEdit,
  onCancel,
  onSave,
}: EnvironmentDetailActionsProps) {
  if (!editing) {
    return (
      <button
        type="button"
        onClick={onEdit}
        className={operatorButtonClass("primary")}
      >
        Edit Details
      </button>
    );
  }

  return (
    <div className="flex gap-2">
      <button
        type="button"
        onClick={onCancel}
        className={operatorButtonClass("secondary")}
      >
        Cancel
      </button>
      <button
        type="button"
        onClick={onSave}
        disabled={saving}
        className={operatorButtonClass("primary")}
      >
        {saving ? "Saving..." : "Save"}
      </button>
    </div>
  );
}

export function EnvironmentProductionNotice() {
  return (
    <OperatorState
      tone="blue"
      title="Environment connected to the IP Center"
      detail="This environment can be used as part of the IP asset library and bound to specific scenes in the episode timeline."
    />
  );
}

export function EnvironmentAuditPanels({
  metadata,
}: {
  metadata?: Environment["metadata"];
}) {
  const envMeta = (metadata ?? {}) as Record<string, unknown>;
  const textToImageWarnings = (
    envMeta["last_text_to_image_generation"] as
      | Record<string, unknown>
      | undefined
  )?.["audit_warnings"];
  const imageToImageWarnings = (
    envMeta["last_image_to_image_generation"] as
      | Record<string, unknown>
      | undefined
  )?.["audit_warnings"];

  return (
    <div className="space-y-3">
      <GenerationAuditWarnings
        title="Environment Text-to-Image Warnings"
        warnings={textToImageWarnings}
      />
      <GenerationAuditWarnings
        title="Environment Image-to-Image Warnings"
        warnings={imageToImageWarnings}
      />
    </div>
  );
}

export function EnvironmentReadinessPanel({
  env,
  imageCount,
  onBack,
}: {
  env: Environment;
  imageCount: number;
  onBack: () => void;
}) {
  const linkedCount = env.linked_virtual_ip_count || 0;
  return (
    <OperatorPanel>
      <OperatorSectionHeader
        title="Association & Generation Status"
        subtitle="IP associations, image library, and generation tasks"
      />
      <div className="space-y-4 p-4">
        <div className="flex items-center justify-between gap-3 text-xs">
          <span className="text-gray-500">IP Association</span>
          <StatusPill tone={linkedCount > 0 ? "green" : "amber"}>
            {linkedCount > 0 ? `${linkedCount} IPs` : "Not linked"}
          </StatusPill>
        </div>
        <div className="flex items-center justify-between gap-3 text-xs">
          <span className="text-gray-500">Environment Images</span>
          <StatusPill tone={imageCount > 0 ? "green" : "gray"}>
            {imageCount > 0 ? "ready" : "empty"}
          </StatusPill>
        </div>
        <div className="flex items-center justify-between gap-3 text-xs">
          <span className="text-gray-500">Generation Access</span>
          <StatusPill tone="blue">available</StatusPill>
        </div>
        <button
          type="button"
          onClick={onBack}
          className={operatorButtonClass("secondary", "w-full")}
        >
          Back to Environment List
        </button>
      </div>
    </OperatorPanel>
  );
}

export function EnvironmentNotFound({ onBack }: { onBack: () => void }) {
  return (
    <OperatorState
      title="Environment not found or deleted"
      detail="Go back to the list to select another environment asset."
      action={
        <button
          type="button"
          onClick={onBack}
          className={operatorButtonClass("secondary")}
        >
          Back to List
        </button>
      }
    />
  );
}
