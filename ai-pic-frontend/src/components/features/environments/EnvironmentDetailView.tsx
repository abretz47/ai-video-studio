"use client";

import { useParams, useRouter } from "next/navigation";

import {
  OperatorPanel,
  OperatorInspector,
  OperatorMainCanvas,
  OperatorSectionHeader,
  OperatorShell,
  OperatorState,
  OperatorWorkspace,
} from "@/components/shared";

import { EnvironmentHeader } from "./EnvironmentHeader";
import { EnvironmentImagesPanel } from "./EnvironmentImagesPanel";
import { EnvironmentSidePanel } from "./EnvironmentSidePanel";
import { useEnvironmentDetailState } from "./EnvironmentDetailState";
import { EnvironmentVariantModal } from "./EnvironmentVariantModal";
import {
  EnvironmentAuditPanels,
  EnvironmentDetailActions,
  EnvironmentProductionNotice,
  EnvironmentNotFound,
  EnvironmentReadinessPanel,
} from "./EnvironmentDetailViewParts";

export function EnvironmentDetailView() {
  const params = useParams();
  const router = useRouter();
  const envKey = params?.id?.toString() || "";
  const state = useEnvironmentDetailState(envKey);

  if (state.loading) {
    return (
      <OperatorShell
        title="Environment Details"
        subtitle="Loading environment assets"
        breadcrumb={["IP Center", "Environment Assets", "Loading"]}
      >
        <OperatorState
          tone="blue"
          title="Loading environment details"
          detail="Reading environment information and the image library."
        />
      </OperatorShell>
    );
  }

  if (!state.env) {
    return (
      <OperatorShell
        title="Environment Details"
        subtitle="Environment Asset Library"
        breadcrumb={["IP Center", "Environment Assets"]}
      >
        <EnvironmentNotFound onBack={() => router.push("/environments")} />
      </OperatorShell>
    );
  }

  return (
    <OperatorShell
      title="Environment Details"
      subtitle={state.env.name}
      breadcrumb={["IP Center", "Environment Assets", state.env.name]}
    >
      <div className="space-y-5">
        <EnvironmentProductionNotice />
        <EnvironmentAuditPanels metadata={state.env.metadata} />
        <OperatorWorkspace
          variant="main-inspector"
          main={
            <OperatorMainCanvas className="space-y-5">
            <OperatorPanel>
              <OperatorSectionHeader
                title="Basic Information"
                subtitle="Category, tags, description, and creation audit"
                action={
                  <EnvironmentDetailActions
                    editing={state.editingMeta}
                    saving={state.savingMeta}
                    onEdit={() => state.setEditingMeta(true)}
                    onCancel={state.handleCancelMeta}
                    onSave={state.handleSaveMeta}
                  />
                }
              />
              <EnvironmentHeader
                env={state.env}
                editing={state.editingMeta}
                form={state.metaForm}
                setForm={state.setMetaForm}
                addTag={state.handleAddTag}
                removeTag={state.handleRemoveTag}
              />
            </OperatorPanel>

            <OperatorPanel>
              <OperatorSectionHeader
                title="Environment Image Library"
                subtitle="Reference images, variant generation, and delete actions"
              />
              <div className="p-4">
                <EnvironmentImagesPanel
                  envName={state.env.name}
                  images={state.images}
                  imageSrc={state.imageSrc}
                  onImg2Img={(image) => state.setVariantTarget(image)}
                  onDelete={state.handleDeleteImage}
                  variant="embedded"
                />
              </div>
            </OperatorPanel>
            </OperatorMainCanvas>
          }
          inspector={
            <OperatorInspector title="Environment Inspector" subtitle="IP associations, generation, and task submission">
            <EnvironmentReadinessPanel
              env={state.env}
              imageCount={state.images.length}
              onBack={() => router.push("/environments")}
            />
            <div className="mt-5 border-t border-gray-200 pt-5">
              <h3 className="text-sm font-semibold text-gray-950">Environment Generation</h3>
              <div className="mt-3">
                <EnvironmentSidePanel
                  envKey={envKey}
                  onImageUploaded={state.handleImageUploaded}
                  onImagesGenerated={state.reload}
                  variant="embedded"
                />
              </div>
            </div>
            </OperatorInspector>
          }
        />
      </div>
      <EnvironmentVariantModal
        envKey={envKey}
        env={state.env}
        target={state.variantTarget}
        imageSrc={state.imageSrc}
        onClose={() => state.setVariantTarget(null)}
      />
    </OperatorShell>
  );
}
