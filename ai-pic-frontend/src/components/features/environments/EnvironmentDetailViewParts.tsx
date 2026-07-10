import { t } from "@/lib/i18n";
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
        {t("environments.parts.edit", "Edit Metadata")}
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
        {t("common.cancel", "Cancel")}
      </button>
      <button
        type="button"
        onClick={onSave}
        disabled={saving}
        className={operatorButtonClass("primary")}
      >
        {saving ? t("common.saving", "Saving...") : t("common.save", "Save")}
      </button>
    </div>
  );
}

export function EnvironmentProductionNotice() {
  return (
    <OperatorState
      tone="blue"
      title={t("environments.parts.noticeTitle", "Environment Linked to IP Center")}
      detail={t("environments.parts.noticeDetail", "Environments can live in the IP asset pool and be bound to specific scenes in an episode timeline.")}
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
        title={t("environments.parts.textToImageWarnings", "Environment Text-to-Image Notes")}
        warnings={textToImageWarnings}
      />
      <GenerationAuditWarnings
        title={t("environments.parts.imageToImageWarnings", "Environment Image-to-Image Notes")}
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
        title={t("environments.parts.readinessTitle", "Link & Generation Status")}
        subtitle={t("environments.parts.readinessSubtitle", "IP links, image pool, and generation tasks")}
      />
      <div className="space-y-4 p-4">
        <div className="flex items-center justify-between gap-3 text-xs">
          <span className="text-gray-500">{t("environments.parts.linkedIp", "IP Links")}</span>
          <StatusPill tone={linkedCount > 0 ? "green" : "amber"}>
            {linkedCount > 0 ? t("environments.parts.linkedIpCount", "{count} linked IPs").replace("{count}", String(linkedCount)) : t("environments.parts.unlinked", "Unlinked")}
          </StatusPill>
        </div>
        <div className="flex items-center justify-between gap-3 text-xs">
          <span className="text-gray-500">{t("environments.parts.images", "Environment Images")}</span>
          <StatusPill tone={imageCount > 0 ? "green" : "gray"}>
            {imageCount > 0 ? t("common.ready", "Ready") : t("common.empty", "Empty")}
          </StatusPill>
        </div>
        <div className="flex items-center justify-between gap-3 text-xs">
          <span className="text-gray-500">{t("environments.parts.entry", "Generation Entry")}</span>
          <StatusPill tone="blue">{t("common.available", "Available")}</StatusPill>
        </div>
        <button
          type="button"
          onClick={onBack}
          className={operatorButtonClass("secondary", "w-full")}
        >
          {t("environments.parts.backToList", "Back to Environment List")}
        </button>
      </div>
    </OperatorPanel>
  );
}

export function EnvironmentNotFound({ onBack }: { onBack: () => void }) {
  return (
    <OperatorState
      title={t("environments.parts.notFoundTitle", "Environment Not Found or Deleted")}
      detail={t("environments.parts.notFoundDetail", "Go back to the list to choose another environment asset.")}
      action={
        <button
          type="button"
          onClick={onBack}
          className={operatorButtonClass("secondary")}
        >
          {t("common.backToList", "Back to List")}
        </button>
      }
    />
  );
}
