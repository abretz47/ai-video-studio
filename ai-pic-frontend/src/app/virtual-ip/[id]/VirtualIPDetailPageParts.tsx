import Link from "next/link";
import type { Dispatch, SetStateAction } from "react";

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
          Virtual IP assets can be used for stories, episodes, and generation tasks, and some fields can still be edited.
        </div>
        <Link href="/virtual-ip" className={operatorButtonClass("ghost")}>
          Back to Virtual IP Projects
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
      <h3 className="mb-3 text-sm font-semibold text-gray-950">Backstory</h3>
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
        <p className="text-sm text-gray-400">Not provided</p>
      )}
    </div>
  );
}

export function VirtualIPMetaStrip({ virtualIP }: { virtualIP: VirtualIP }) {
  return (
    <div className="bg-gray-50/60 p-5">
      <div className="grid gap-3 text-xs text-gray-600 md:grid-cols-3">
        <MetaItem
          label="Creator"
          value={resolveCreatorLabel(virtualIP.creator)}
        />
        <MetaItem label="Created At" value={formatDate(virtualIP.created_at)} />
        <MetaItem
          label="Updated At"
          value={virtualIP.updated_at ? formatDate(virtualIP.updated_at) : "-"}
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
        {ready ? "Ready" : "Needs more"}
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
    <OperatorInspector title="IP Inspector" subtitle="Production readiness, assets, and editing actions">
      <div className="space-y-5">
        <section>
          <h3 className="text-sm font-semibold text-gray-950">Production Readiness Check</h3>
          <div className="mt-3 space-y-3 text-sm">
            <ReadinessRow label="Virtual IP Profile" ready={Boolean(virtualIP.name)} />
            <ReadinessRow
              label="Backstory"
              ready={Boolean(virtualIP.background_story)}
            />
            <ReadinessRow
              label="Voice"
              ready={Boolean(virtualIP.voice_config?.voice_id)}
            />
            <ReadinessRow
              label="Visual Assets"
              ready={Boolean(virtualIP.default_avatar_url)}
            />
            <ReadinessRow label="Environment Assets" ready={linkedEnvironmentCount > 0} />
          </div>
        </section>
        <section className="border-t border-gray-200 pt-4">
          <h3 className="text-sm font-semibold text-gray-950">Asset Management</h3>
          <div className="mt-3 space-y-3">
            <a
              href="#ip-images"
              className={operatorButtonClass("secondary", "w-full")}
            >
              Image Management
            </a>
            <a
              href="#ip-environments"
              className={operatorButtonClass("secondary", "w-full")}
            >
              Environment Assets
            </a>
            {editing ? (
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setEditing(false)}
                  className={operatorButtonClass("secondary")}
                >
                  Cancel Editing
                </button>
                <button
                  type="submit"
                  form={editFormId}
                  className={operatorButtonClass("primary")}
                >
                  Save
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setEditing(true)}
                className={operatorButtonClass("primary", "w-full")}
              >
                Edit Virtual IP
              </button>
            )}
            <button
              type="button"
              onClick={onDelete}
              className="h-8 rounded-md px-2 text-xs font-medium text-red-600 hover:bg-red-50"
            >
              Delete Virtual IP
            </button>
          </div>
        </section>
      </div>
    </OperatorInspector>
  );
}

const formatDate = (value: string) => new Date(value).toLocaleString("zh-CN");

function MetaItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span className="font-medium">{label}: </span>
      {value}
    </div>
  );
}
