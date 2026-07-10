"use client";

import { useCallback, useEffect, useState } from "react";
import { virtualIPAPI } from "@/utils/api/endpoints";
import type { VirtualIP } from "@/utils/api/types";
import { useVirtualIPDetailVoice } from "./useVirtualIPDetailVoice";

export interface UseVirtualIPDetailOptions {
  ipKey: string;
  showAlert: (opts: {
    message: string;
    variant: "success" | "error" | "warning" | "info";
    title?: string;
    confirmText?: string;
    onConfirm?: () => void;
  }) => void;
  router: { push: (path: string) => void };
}

export interface EditFormState {
  name: string;
  description: string;
  tags: string[];
  background_story: string;
  biography: string;
  style_prompt: string;
  style_reference_images: string[];
  is_active: boolean;
  is_public: boolean;
}

export function useVirtualIPDetail({
  ipKey,
  showAlert,
  router,
}: UseVirtualIPDetailOptions) {
  // Core state
  const [virtualIP, setVirtualIP] = useState<VirtualIP | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState<EditFormState>({
    name: "",
    description: "",
    tags: [],
    background_story: "",
    biography: "",
    style_prompt: "",
    style_reference_images: [],
    is_active: true,
    is_public: false,
  });

  const {
    voiceEnums,
    voiceTypeFilter,
    setVoiceTypeFilter,
    voiceSettings,
    setVoiceSettings,
    voicePreviewText,
    setVoicePreviewText,
    voiceLoading,
    previewLoading,
    previewAudioUrl,
    voiceOptions,
    syncVirtualIPVoice,
    handlePreviewVoice,
  } = useVirtualIPDetailVoice({
    showAlert,
    virtualIPName: virtualIP?.name,
  });

  // Fetch virtual IP
  const fetchVirtualIP = useCallback(async () => {
    try {
      setLoading(true);
      const response = await virtualIPAPI.getVirtualIP(ipKey);

      if (response.success && response.data) {
        setVirtualIP(response.data);
        setEditForm({
          name: response.data.name,
          description: response.data.description || "",
          tags: response.data.tags || [],
          background_story: response.data.background_story || "",
          biography: response.data.biography || "",
          style_prompt: response.data.style_prompt || "",
          style_reference_images: response.data.style_reference_images || [],
          is_active: response.data.is_active ?? true,
          is_public: response.data.is_public ?? false,
        });
        syncVirtualIPVoice(response.data);
      } else {
        console.error("Failed to fetch virtual IP:", response.error);
        showAlert({ message: "Failed to fetch Virtual IP", variant: "error" });
      }
    } catch (error) {
      console.error("Error fetching virtual IP:", error);
      showAlert({ message: "Failed to fetch Virtual IP", variant: "error" });
    } finally {
      setLoading(false);
    }
  }, [ipKey, showAlert, syncVirtualIPVoice]);

  // Update virtual IP
  const handleUpdateIP = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const identifier = virtualIP?.business_id || ipKey;
      const response = await virtualIPAPI.updateVirtualIP(identifier, {
        ...editForm,
        voice_config: voiceSettings,
      });
      if (response.success && response.data) {
        setVirtualIP(response.data);
        setEditing(false);
        showAlert({ message: "Updated successfully", variant: "success" });
      } else {
        showAlert({
          message: `Update failed: ${response.error || "Unknown error"}`,
          variant: "error",
        });
      }
    } catch (error) {
      console.error("Error updating virtual IP:", error);
      showAlert({
        message: "Update failed. Please try again later.",
        variant: "error",
      });
    }
  };

  // Delete virtual IP
  const handleDeleteIP = () => {
    showAlert({
      title: "Confirm Virtual IP deletion",
      message: "Are you sure you want to delete this Virtual IP? This action cannot be undone!",
      variant: "warning",
      confirmText: "Delete",
      onConfirm: async () => {
        try {
          const identifier = virtualIP?.business_id || ipKey;
          const response = await virtualIPAPI.deleteVirtualIP(identifier);
          if (response.success) {
            showAlert({ message: "Deleted successfully", variant: "success" });
            router.push("/virtual-ip");
          } else {
            showAlert({
              message: `Deletion failed: ${response.error || "Unknown error"}`,
              variant: "error",
            });
          }
        } catch (error) {
          console.error("Error deleting virtual IP:", error);
          showAlert({
            message: "Deletion failed. Please try again later.",
            variant: "error",
          });
        }
      },
    });
  };

  // Tag management
  const addTag = (tag: string) => {
    if (tag && !editForm.tags.includes(tag)) {
      setEditForm({ ...editForm, tags: [...editForm.tags, tag] });
    }
  };

  const removeTag = (tagToRemove: string) => {
    setEditForm({
      ...editForm,
      tags: editForm.tags.filter((tag) => tag !== tagToRemove),
    });
  };

  // Effects
  useEffect(() => {
    if (ipKey) {
      void fetchVirtualIP();
    }
  }, [fetchVirtualIP, ipKey]);

  return {
    // Core state
    virtualIP,
    loading,
    editing,
    setEditing,
    editForm,
    setEditForm,

    // Voice state
    voiceEnums,
    voiceTypeFilter,
    setVoiceTypeFilter,
    voiceSettings,
    setVoiceSettings,
    voicePreviewText,
    setVoicePreviewText,
    voiceLoading,
    previewLoading,
    previewAudioUrl,
    voiceOptions,

    // Handlers
    handleUpdateIP,
    handleDeleteIP,
    addTag,
    removeTag,
    handlePreviewVoice,
  };
}
