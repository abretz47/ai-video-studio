"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { virtualIPAPI } from "@/utils/api/endpoints";
import type { VirtualIP } from "@/utils/api/types";
import type { AlertOptions } from "@/components/shared/modals/AlertModalProvider";

interface UseVirtualIPListOptions {
  showAlert: (options: AlertOptions) => void;
}

export function useVirtualIPList({ showAlert }: UseVirtualIPListOptions) {
  const [virtualIPs, setVirtualIPs] = useState<VirtualIP[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  const fetchVirtualIPs = useCallback(async () => {
    try {
      setLoading(true);
      const response = await virtualIPAPI.getVirtualIPs({
        search: searchTerm || undefined,
        tags: selectedTags.length > 0 ? selectedTags : undefined,
      });

      if (response.success && response.data) {
        setVirtualIPs(response.data);
      } else {
        console.error("Failed to fetch virtual IP list:", response.error);
      }
    } catch (error) {
      console.error("Error fetching virtual IP list:", error);
    } finally {
      setLoading(false);
    }
  }, [searchTerm, selectedTags]);

  useEffect(() => {
    void fetchVirtualIPs();
  }, [fetchVirtualIPs]);

  const allTags = useMemo(
    () => Array.from(new Set(virtualIPs.flatMap((ip) => ip.tags ?? []))),
    [virtualIPs],
  );

  const toggleTag = useCallback((tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag],
    );
  }, []);

  const deleteVirtualIPById = useCallback(
    async (bizId: string) => {
      try {
        const response = await virtualIPAPI.deleteVirtualIP(bizId);
        if (response.success) {
          setVirtualIPs((prev) =>
            prev.filter((ip) => ip.business_id !== bizId),
          );
        } else {
          showAlert({
            message: `DeleteFailed: ${response.error || "Unknown error"}`,
            variant: "error",
          });
        }
      } catch (error) {
        console.error("Error deleting virtual IP:", error);
        showAlert({ message: "Delete failed. Please retry", variant: "error" });
      }
    },
    [showAlert],
  );

  const handleDeleteIP = useCallback(
    (bizId: string) => {
      showAlert({
        title: "Confirm Delete Virtual IP",
        message: "Delete this virtual IP?",
        variant: "warning",
        confirmText: "Delete",
        onConfirm: () => {
          void deleteVirtualIPById(bizId);
        },
      });
    },
    [deleteVirtualIPById, showAlert],
  );

  const prependVirtualIP = useCallback((virtualIP: VirtualIP) => {
    setVirtualIPs((prev) => [virtualIP, ...prev]);
  }, []);

  return {
    virtualIPs,
    loading,
    searchTerm,
    setSearchTerm,
    selectedTags,
    toggleTag,
    allTags,
    handleDeleteIP,
    prependVirtualIP,
  };
}
