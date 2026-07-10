import Link from "next/link";
import type { Dispatch, SetStateAction } from "react";
import { formatDateTime, t } from "@/lib/i18n";
import {
  OperatorPanel,
  OperatorInspector,
  StatusPill,
  operatorButtonClass,
  operatorInputClass,
} from "@/components/shared";
import { CollapsibleText } from "@/components/ui";
import type { EditFormState } from "@/hooks/useVirtualIPDetail";
import type { VirtualIP } from "@/utils/api/types";
import { resolveCreatorLabel } from "@/utils/creator";

export function VirtualIPProductionNotice() {
  return (
    <OperatorPanel className="p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="text-xs text-blue-700">
          {t("virtualIp.detail.notice", "IP assets can power stories, episodes, and generation tasks, and some fields remain editable.")}
        </div>
        <Link href="/virtual-ip" className={operatorButtonClass("ghost")}>
          {t("virtualIp.detail.backToProjects", "Back to IP projects")}
        </Link>
      </div>
    </OperatorPanel>
  );
}

export function VirtualIPBackgroundStorySection({
  virtualIP,
  editing,
  editForm,
  setEditForm,
}: {
  virtualIP: VirtualIP;
  editing: boolean;
  editForm: EditFormState;
  setEditForm: Dispatch<SetStateAction<EditFormState>>;
}) {
  if (!editing && !virtualIP.background_story) return null;
  return (
    <div className="border-b border-gray-100 p-5">
      <h3 className="mb-3 text-sm font-semibold text-gray-950">{t("virtualIp.detail.backgroundStory", "Background Story")}</h3>
      {editing ? (
        <textarea
          value={editForm.background_story}
          onChange={(event) =>
            setEditForm({ ...editForm, background_story: event.target.value })
          }
          className={operatorInputClass("h-auto min-h-36 w-full py-2 text-sm")}
          rows={6}
        />
      ) : virtualIP.background_story ? (
        <CollapsibleText text={virtualIP.background_story} collapsedLines={4} />
      ) : (
        <p className="text-sm text-gray-400">{t("common.notFilled", "Not filled")}</p>
      )}
    </div>
  );
}

export function VirtualIPMetaStrip({ virtualIP }: { virtualIP: VirtualIP }) {
  return (
    <div className="bg-gray-50/60 p-5">
      <div className="grid gap-3 text-xs text-gray-600 md:grid-cols-3">
        <MetaItem
          label={t("common.creator", "Creator")}
          value={resolveCreatorLabel(virtualIP.creator)}
        />
        <MetaItem label={t("common.createdAt", "Created")}
          value={formatDateTime(virtualIP.created_at)} />
        <MetaItem
          label={t("common.updatedAt", "Updated")}
          value={virtualIP.updated_at ? formatDateTime(virtualIP.updated_at) : "-"}
        />
      </div>
    </div>
  );
}

function ReadinessRow({ label, ready }: { label: string; ready: boolean }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="text-gray-600">{label}</span>
      <StatusPill tone={ready ? "green" : "amber"}>
        {ready ? t("common.status.passed", "Passed") : t("common.status.needsInput", "Needs input")}
      </StatusPill>
    </div>
  );
}

export function VirtualIPInspectorPanel({
  virtualIP,
  editing,
  editFormId,
  linkedEnvironmentCount,
  setEditing,
  onDelete,
}: {
  virtualIP: VirtualIP;
  editing: boolean;
  editFormId: string;
  linkedEnvironmentCount: number;
  setEditing: (editing: boolean) => void;
  onDelete: () => void;
}) {
  return (
    <OperatorInspector title={t("virtualIp.detail.inspectorTitle", "IP Inspector")} subtitle={t("virtualIp.detail.inspectorSubtitle", "Production readiness, assets, and edit actions")}>
      <div className="space-y-5">
        <section>
          <h3 className="text-sm font-semibold text-gray-950">{t("virtualIp.detail.readinessTitle", "Production readiness checks")}</h3>
          <div className="mt-3 space-y-3 text-sm">
            <ReadinessRow label={t("virtualIp.detail.readiness.profile", "IP profile")} ready={Boolean(virtualIP.name)} />
            <ReadinessRow
              label={t("virtualIp.detail.readiness.background", "Background story")}
              ready={Boolean(virtualIP.background_story)}
            />
            <ReadinessRow
              label={t("virtualIp.detail.readiness.voice", "Voice")}
              ready={Boolean(virtualIP.voice_config?.voice_id)}
            />
            <ReadinessRow
              label={t("virtualIp.detail.readiness.avatar", "Visual asset")}
              ready={Boolean(virtualIP.default_avatar_url)}
            />
            <ReadinessRow label={t("virtualIp.detail.readiness.environments", "Environment assets")} ready={linkedEnvironmentCount > 0} />
          </div>
        </section>
        <section className="border-t border-gray-200 pt-4">
          <h3 className="text-sm font-semibold text-gray-950">{t("virtualIp.detail.assetManagement", "Asset Management")}</h3>
          <div className="mt-3 space-y-3">
            <a
              href="#ip-images"
              className={operatorButtonClass("secondary", "w-full")}
            >
              {t("virtualIp.detail.manageImages", "Manage Images")}
            </a>
            <a
              href="#ip-environments"
              className={operatorButtonClass("secondary", "w-full")}
            >
              {t("virtualIp.detail.environmentAssets", "Environment Assets")}
            </a>
            {editing ? (
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setEditing(false)}
                  className={operatorButtonClass("secondary")}
                >
                  {t("virtualIp.detail.cancelEdit", "Cancel Edit")}
                </button>
                <button
                  type="submit"
                  form={editFormId}
                  className={operatorButtonClass("primary")}
                >
                  {t("common.save", "Save")}
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setEditing(true)}
                className={operatorButtonClass("primary", "w-full")}
              >
                {t("virtualIp.detail.editIp", "Edit IP")}
              </button>
            )}
            <button
              type="button"
              onClick={onDelete}
              className="h-8 rounded-md px-2 text-xs font-medium text-red-600 hover:bg-red-50"
            >
              {t("common.deleteIp", "Delete IP")}
            </button>
          </div>
        </section>
      </div>
    </OperatorInspector>
  );
}

function MetaItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span className="font-medium">{label}: </span>
      {value}
    </div>
  );
}
