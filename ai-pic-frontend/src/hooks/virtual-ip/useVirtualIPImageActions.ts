import { virtualIPImageAPI } from "@/utils/api/endpoints";
import type { VirtualIPImage } from "@/utils/api/types";

interface UseVirtualIPImageActionsOptions {
  virtualIPId: number | null;
  setImages: React.Dispatch<React.SetStateAction<VirtualIPImage[]>>;
  showAlert: (opts: {
    message: string;
    variant: "success" | "error" | "warning" | "info";
    title?: string;
    confirmText?: string;
    onConfirm?: () => void;
  }) => void;
}

export function useVirtualIPImageActions({
  virtualIPId,
  setImages,
  showAlert,
}: UseVirtualIPImageActionsOptions) {
  const handleDeleteImage = (imageId: number) => {
    showAlert({
      title: "Confirm image deletion",
      message: "Are you sure you want to delete this image?",
      variant: "warning",
      confirmText: "Delete",
      onConfirm: async () => {
        if (!virtualIPId) {
          showAlert({
            message: "Virtual IP has not loaded yet",
            variant: "error",
          });
          return;
        }
        try {
          const response = await virtualIPImageAPI.deleteImage(
            virtualIPId,
            imageId,
          );
          if (response.success) {
            setImages((prev) => prev.filter((img) => img.id !== imageId));
            showAlert({ message: "Image deleted successfully", variant: "success" });
          } else {
            throw new Error(response.error || "Failed to delete image");
          }
        } catch (error) {
          console.error("Delete image failed:", error);
          showAlert({
            message: `Failed to delete image: ${
              error instanceof Error ? error.message : "Unknown error"
            }`,
            variant: "error",
          });
        }
      },
    });
  };

  const handleSetDefault = async (imageId: number) => {
    if (!virtualIPId) {
      showAlert({ message: "Virtual IP has not loaded yet", variant: "error" });
      return;
    }
    try {
      const response = await virtualIPImageAPI.setDefaultImage(
        virtualIPId,
        imageId,
      );
      if (response.success) {
        setImages((prev) =>
          prev.map((img) => ({ ...img, is_default: img.id === imageId })),
        );
        showAlert({ message: "Default image set", variant: "success" });
      } else {
        throw new Error(response.error || "Failed to set default image");
      }
    } catch (error) {
      console.error("Set default image failed:", error);
      showAlert({
        message: `Failed to set default image: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
        variant: "error",
      });
    }
  };

  return { handleDeleteImage, handleSetDefault };
}
