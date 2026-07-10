"use client";
import { useRouter } from "next/navigation";
import { aiAPI } from "@/utils/api/endpoints";
import { AIModelType, type VirtualIP } from "@/utils/api/types";
import {
  OperatorPanel,
  OperatorSectionHeader,
  OperatorState,
  operatorButtonClass,
} from "@/components/shared";
import {
  ImagePreviewModal,
  ImageToImageModal,
  useAlertModal,
} from "@/components/shared/modals";
import {
  resolveImageUrl,
  useVirtualIPImages,
  VIRTUAL_IP_STYLE_SPEC_FIELDS,
} from "@/hooks/useVirtualIPImages";
import { CategoryFilter } from "./CategoryFilter";
import { ImageGenerationForm } from "./ImageGenerationForm";
import { ImageGrid } from "./ImageGrid";
import { ImageUploadForm } from "./ImageUploadForm";
interface VirtualIPImageManagerProps {
  virtualIPKey: string;
  virtualIP?: VirtualIP | null;
}
export function VirtualIPImageManager({
  virtualIPKey,
  virtualIP,
}: VirtualIPImageManagerProps) {
  const router = useRouter();
  const { showAlert } = useAlertModal();
  const state = useVirtualIPImages({
    virtualIPKey,
    virtualIP,
    skipVirtualIPFetch: Boolean(virtualIP),
    showAlert,
    router,
  });

  const {
    virtualIP: fetchedVirtualIP,
    virtualIPId,
    categories,
    selectedCategory,
    setSelectedCategory,
    loading,
    generating,
    uploading,
    filteredImages,
    preview,
    setPreview,
    showGenerateForm,
    setShowGenerateForm,
    generateForm,
    setGenerateForm,
    stylePresets,
    selectedStylePreset,
    selectedModel,
    uploadForm,
    setUploadForm,
    variantTarget,
    variantPrompt,
    variantModalOpen,
    setVariantModalOpen,
    variantSubmitting,
    variantReferenceSections,
    handleGenerateImage,
    handleUploadImage,
    handleDeleteImage,
    handleSetDefault,
    handleOpenVariant,
    handleSubmitVariant,
  } = state;

  const activeVirtualIP = virtualIP || fetchedVirtualIP;

  if (!activeVirtualIP && loading) {
    return (
      <section id="ip-images" className="scroll-mt-24">
        <OperatorState title="Loading image manager..." />
      </section>
    );
  }

  if (!activeVirtualIP) {
    return null;
  }

  return (
    <section id="ip-images" className="scroll-mt-24">
      <OperatorPanel className="overflow-hidden">
        <OperatorSectionHeader
          title={`${activeVirtualIP.name} - Image Manager`}
          subtitle="Manage portraits, upper-body shots, action shots, and reference images for this IP"
          action={
            <button
              type="button"
              onClick={() => router.push("/tasks")}
              className={operatorButtonClass("secondary")}
            >
              View Tasks
            </button>
          }
        />
        <div className="grid gap-4 p-4 lg:grid-cols-[160px_minmax(0,1fr)]">
          <aside className="min-w-0 space-y-4">
            <CategoryFilter
              categories={categories}
              selectedCategory={selectedCategory}
              onSelectCategory={setSelectedCategory}
            />
            <OperatorState
              title="Image Assets"
              detail="These image assets will carry over into story production for this IP."
              tone="blue"
            />
          </aside>
          <div className="min-w-0">
            {loading ? (
              <OperatorState title="Loading images..." />
            ) : (
              <ImageGrid
                images={filteredImages}
                virtualIP={activeVirtualIP}
                onPreview={(image) =>
                  setPreview({
                    src: resolveImageUrl(image),
                    alt: `${activeVirtualIP.name} - ${image.category}`,
                    description: `${image.category} | ${new Date(
                      image.created_at,
                    ).toLocaleString()}`,
                  })
                }
                onImg2Img={handleOpenVariant}
                onDelete={handleDeleteImage}
                onSetDefault={handleSetDefault}
              />
            )}
          </div>
          <aside className="min-w-0 rounded-lg border border-gray-200 bg-white p-4 lg:col-span-2">
            <div className="mb-4 flex gap-2">
              <button
                type="button"
                onClick={() => setShowGenerateForm(true)}
                className={operatorButtonClass(
                  showGenerateForm ? "primary" : "secondary",
                )}
              >
                Generate Images
              </button>
              <button
                type="button"
                onClick={() => setShowGenerateForm(false)}
                className={operatorButtonClass(
                  !showGenerateForm ? "primary" : "secondary",
                )}
              >
                Upload
              </button>
            </div>
            {showGenerateForm ? (
              <ImageGenerationForm
                virtualIPId={virtualIPId}
                generateForm={generateForm}
                setGenerateForm={setGenerateForm}
                stylePresets={stylePresets}
                selectedStylePreset={selectedStylePreset}
                selectedModel={selectedModel}
                generating={generating}
                onGenerate={handleGenerateImage}
                onCancel={() => setShowGenerateForm(false)}
              />
            ) : (
              <ImageUploadForm
                uploadForm={uploadForm}
                setUploadForm={setUploadForm}
                uploading={uploading}
                onUpload={handleUploadImage}
              />
            )}
          </aside>
        </div>

        <ImageToImageModal
          open={variantModalOpen && !!variantTarget}
          onClose={() => {
            setVariantModalOpen(false);
          }}
          title="Image-to-Image Variant"
          description="Submit the reference image and prompt as an image-to-image task, with adjustable model, resolution, and output count."
          referenceSections={variantReferenceSections}
          defaultSelected={variantReferenceSections.flatMap(
            (section) => section.images,
          )}
          lockSelection
          defaultPrompt={variantPrompt}
          defaultModel={
            (variantTarget?.ai_model as string | undefined) ||
            generateForm.model ||
            ""
          }
          defaultGenerationProfileId={generateForm.generation_profile || ""}
          defaultCount={1}
          defaultSize={generateForm.size || ""}
          defaultAspectRatio={generateForm.aspect_ratio || ""}
          defaultStylePresetId={generateForm.style_preset_id || ""}
          defaultStyleSpec={generateForm.style_spec || {}}
          styleSpecFields={VIRTUAL_IP_STYLE_SPEC_FIELDS}
          modelType={AIModelType.ImageToImage}
          modelFetcher={() =>
            aiAPI.getAvailableModels({ type: AIModelType.ImageToImage })
          }
          modelCacheKey={`virtual-ip-img2img:${virtualIPId}`}
          showAdvancedParams
          defaultAdvancedValue={{
            seed: generateForm.seed,
            steps: generateForm.steps,
            cfg_scale: generateForm.cfg_scale,
          }}
          submitting={variantSubmitting}
          onSubmit={handleSubmitVariant}
        />

        <ImagePreviewModal
          open={!!preview}
          src={preview?.src || ""}
          alt={preview?.alt}
          description={preview?.description}
          onClose={() => setPreview(null)}
        />
      </OperatorPanel>
    </section>
  );
}
