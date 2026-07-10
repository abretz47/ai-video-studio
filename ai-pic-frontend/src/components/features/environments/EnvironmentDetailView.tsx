"use client";

import { useParams, useRouter } from "next/navigation";
import { t } from "@/lib/i18n";
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
        title={t("environments.detail.pageTitle", "Environment Details")}
        subtitle={t("environments.detail.loadingSubtitle", "Loading environment assets")}
        breadcrumb={[
          t("common.breadcrumb.ipCenter", "IP Center"),
          t("environments.page.breadcrumb", "Environment Assets"),
          t("common.loading", "Loading"),
        ]}
      >
        <OperatorState
          tone="blue"
          title={t("environments.detail.loadingTitle", "Loading environment details")}
          detail={t("environments.detail.loadingDetail", "Reading environment metadata and image pool.")}
        />
      </OperatorShell>
    );
  }

  if (!state.env) {
    return (
      <OperatorShell
        title={t("environments.detail.pageTitle", "Environment Details")}
        subtitle={t("environments.detail.poolSubtitle", "Environment asset pool")}
        breadcrumb={[
          t("common.breadcrumb.ipCenter", "IP Center"),
          t("environments.page.breadcrumb", "Environment Assets"),
        ]}
      >
        <EnvironmentNotFound onBack={() => router.push("/environments")} />
      </OperatorShell>
    );
  }

  return (
    <OperatorShell
      title={t("environments.detail.pageTitle", "Environment Details")}
      subtitle={state.env.name}
      breadcrumb={[
        t("common.breadcrumb.ipCenter", "IP Center"),
        t("environments.page.breadcrumb", "Environment Assets"),
        state.env.name,
      ]}
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
                  title={t("environments.detail.basicInfo", "Basic Information")}
                  subtitle={t("environments.detail.basicInfoSubtitle", "Category, tags, description, and creation audit")}
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
                  title={t("environments.detail.imagePool", "Environment Image Pool")}
                  subtitle={t("environments.detail.imagePoolSubtitle", "Reference images, variant generation, and delete actions")}
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
            <OperatorInspector title={t("environments.detail.inspectorTitle", "Environment Inspector")} subtitle={t("environments.detail.inspectorSubtitle", "IP links, generation, and task submission")}>
              <EnvironmentReadinessPanel
                env={state.env}
                imageCount={state.images.length}
                onBack={() => router.push("/environments")}
              />
              <div className="mt-5 border-t border-gray-200 pt-5">
                <h3 className="text-sm font-semibold text-gray-950">{t("environments.detail.generationTitle", "Environment Generation")}</h3>
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
