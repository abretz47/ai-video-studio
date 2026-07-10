import { t } from "@/lib/i18n";
import { ImagePreviewCard, OperatorState } from "@/components/shared";
import type { EnvironmentImage } from "./types";

interface EnvironmentImagesPanelProps {
  envName: string;
  images: EnvironmentImage[];
  imageSrc: (url: string) => string;
  onImg2Img: (image: EnvironmentImage) => void;
  onDelete: (url: string) => void;
  variant?: "card" | "embedded";
}

export function EnvironmentImagesPanel({
  envName,
  images,
  imageSrc,
  onImg2Img,
  onDelete,
  variant = "card",
}: EnvironmentImagesPanelProps) {
  const containerClassName =
    variant === "embedded"
      ? "space-y-4"
      : "space-y-4 rounded-lg border border-gray-200 bg-white p-4 lg:col-span-2";

  return (
    <div className={containerClassName}>
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-gray-950">{t("environments.images.title", "Image Pool")}</h3>
        <span className="text-xs text-gray-500">{t("environments.images.count", "{count} images").replace("{count}", String(images.length))}</span>
      </div>
      {images.length === 0 ? (
        <OperatorState
          title={t("environments.images.emptyTitle", "No Reference Images Yet")}
          detail={t("environments.images.emptyDetail", "Images will appear in the environment asset pool after upload or generation.")}
        />
      ) : (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
          {images.map((img) => (
            <ImagePreviewCard
              key={img.url}
              src={imageSrc(img.url)}
              alt={envName}
              showActionsOnHover
              onImg2Img={() => onImg2Img(img)}
              onDelete={() => onDelete(img.url)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
