import { useCallback, useEffect, useMemo, useState } from "react";

import { useAlertModal } from "@/components/shared/modals";
import { storyStructureAPI } from "@/utils/api/endpoints";
import type { Environment } from "@/utils/api/types";

import type { EnvironmentImage } from "./types";

export function useEnvironmentDetailState(envKey: string) {
  const { showAlert } = useAlertModal();
  const [env, setEnv] = useState<Environment | null>(null);
  const [images, setImages] = useState<EnvironmentImage[]>([]);
  const [loading, setLoading] = useState(true);
  const [variantTarget, setVariantTarget] = useState<EnvironmentImage | null>(
    null,
  );
  const [editingMeta, setEditingMeta] = useState(false);
  const [savingMeta, setSavingMeta] = useState(false);
  const [metaForm, setMetaForm] = useState({
    category: "",
    tags: [] as string[],
    description: "",
  });

  const apiBase = useMemo(
    () => (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, ""),
    [],
  );

  const imageSrc = useCallback(
    (url: string) => {
      if (!url) return "";
      if (url.startsWith("http")) return url;
      return `${apiBase}${url.startsWith("/") ? url : `/${url}`}`;
    },
    [apiBase],
  );

  const load = useCallback(async () => {
    if (!envKey) return;
    try {
      setLoading(true);
      const [envRes, imgRes] = await Promise.all([
        storyStructureAPI.getEnvironment(envKey),
        storyStructureAPI.listEnvironmentImages(envKey),
      ]);
      if (envRes.success && envRes.data) {
        setEnv(envRes.data);
      } else {
        showAlert({ message: envRes.error || "Failed to load environment", variant: "error" });
      }
      setImages(imgRes.success && imgRes.data ? imgRes.data.images || [] : []);
    } catch (error) {
      console.error(error);
      showAlert({ message: "Failed to load environment details", variant: "error" });
    } finally {
      setLoading(false);
    }
  }, [envKey, showAlert]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!env || editingMeta) return;
    setMetaForm({
      category: env.category || "",
      tags: env.tags || [],
      description: env.description || "",
    });
  }, [env, editingMeta]);

  const handleDeleteImage = useCallback(
    (url: string) => {
      if (!envKey) return;
      showAlert({
        title: "Confirm Deletion",
        message: "Are you sure you want to delete this reference image?",
        variant: "warning",
        confirmText: "Delete",
        onConfirm: async () => {
          const res = await storyStructureAPI.deleteEnvironmentImage(envKey, url);
          if (res.success && res.data) {
            setImages(res.data.images ?? []);
            showAlert({ message: "Deleted successfully", variant: "success" });
          } else {
            showAlert({ message: res.error || "Delete failed", variant: "error" });
          }
        },
      });
    },
    [envKey, showAlert],
  );

  const handleAddTag = useCallback((tag: string) => {
    const trimmed = tag.trim();
    if (!trimmed) return;
    setMetaForm((prev) =>
      prev.tags.includes(trimmed)
        ? prev
        : { ...prev, tags: [...prev.tags, trimmed] },
    );
  }, []);

  const handleRemoveTag = useCallback((tag: string) => {
    setMetaForm((prev) => ({
      ...prev,
      tags: prev.tags.filter((item) => item !== tag),
    }));
  }, []);

  const handleCancelMeta = useCallback(() => {
    if (env) {
      setMetaForm({
        category: env.category || "",
        tags: env.tags || [],
        description: env.description || "",
      });
    }
    setEditingMeta(false);
  }, [env]);

  const handleSaveMeta = useCallback(async () => {
    if (!envKey) return;
    try {
      setSavingMeta(true);
      const res = await storyStructureAPI.updateEnvironment(envKey, {
        category: metaForm.category,
        tags: metaForm.tags,
        description: metaForm.description,
      });
      if (res.success && res.data) {
        setEnv(res.data);
        setEditingMeta(false);
        showAlert({ message: "Environment details updated", variant: "success" });
      } else {
        showAlert({ message: res.error || "Update failed", variant: "error" });
      }
    } catch (error) {
      console.error(error);
      showAlert({ message: "Update failed", variant: "error" });
    } finally {
      setSavingMeta(false);
    }
  }, [envKey, metaForm, showAlert]);

  const handleImageUploaded = useCallback((url: string) => {
    setImages((prev) => [{ url }, ...prev]);
  }, []);

  return {
    editingMeta,
    env,
    handleAddTag,
    handleCancelMeta,
    handleDeleteImage,
    handleImageUploaded,
    handleRemoveTag,
    handleSaveMeta,
    imageSrc,
    images,
    loading,
    metaForm,
    reload: load,
    savingMeta,
    setEditingMeta,
    setMetaForm,
    setVariantTarget,
    variantTarget,
  };
}
