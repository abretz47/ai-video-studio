"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  OperatorPanel,
  OperatorSectionHeader,
  OperatorState,
  StatusPill,
  operatorButtonClass,
  operatorInputClass,
  operatorSelectClass,
} from "@/components/shared";
import { useAlertModal } from "@/components/shared/modals";
import { storyStructureAPI, virtualIPAPI } from "@/utils/api/endpoints";
import type {
  Environment,
  VirtualIP,
  VirtualIPEnvironmentLink,
} from "@/utils/api/types";
import { availableEnvironmentOptions } from "./virtualIPEnvironmentModel";

interface VirtualIPEnvironmentPanelProps {
  virtualIP: VirtualIP;
  onLinkedCountChange?: (count: number) => void;
}

export function VirtualIPEnvironmentPanel({
  virtualIP,
  onLinkedCountChange,
}: VirtualIPEnvironmentPanelProps) {
  const { showAlert } = useAlertModal();
  const ipKey = virtualIP.business_id || virtualIP.id;
  const [links, setLinks] = useState<VirtualIPEnvironmentLink[]>([]);
  const [environments, setEnvironments] = useState<Environment[]>([]);
  const [loading, setLoading] = useState(true);
  const [linking, setLinking] = useState(false);
  const [selectedEnvId, setSelectedEnvId] = useState("");
  const [quickName, setQuickName] = useState("");
  const [quickCategory, setQuickCategory] = useState("indoor");

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const [linksRes, envRes] = await Promise.all([
        virtualIPAPI.listVirtualIPEnvironments(ipKey),
        storyStructureAPI.listEnvironments(),
      ]);
      if (linksRes.success && linksRes.data) {
        setLinks(linksRes.data);
        onLinkedCountChange?.(linksRes.data.length);
      } else {
        showAlert({ message: linksRes.error || "Failed to load IP environments", variant: "error" });
      }
      setEnvironments(envRes.success && envRes.data ? envRes.data : []);
    } finally {
      setLoading(false);
    }
  }, [ipKey, onLinkedCountChange, showAlert]);

  useEffect(() => {
    void load();
  }, [load]);

  const availableEnvironments = useMemo(
    () => availableEnvironmentOptions(environments, links),
    [environments, links],
  );

  const refreshLinks = (next: VirtualIPEnvironmentLink[]) => {
    setLinks(next);
    onLinkedCountChange?.(next.length);
  };

  const handleLinkExisting = async () => {
    const environmentId = Number(selectedEnvId);
    if (!environmentId) return;
    setLinking(true);
    try {
      const res = await virtualIPAPI.linkVirtualIPEnvironment(ipKey, {
        environment_id: environmentId,
      });
      if (res.success && res.data) {
        refreshLinks([...links.filter((item) => item.environment_id !== environmentId), res.data]);
        setSelectedEnvId("");
        showAlert({ message: "Environment linked to IP", variant: "success" });
      } else {
        showAlert({ message: res.error || "Failed to link environment", variant: "error" });
      }
    } finally {
      setLinking(false);
    }
  };

  const handleQuickCreate = async () => {
    const name = quickName.trim();
    if (!name) return;
    setLinking(true);
    try {
      const created = await storyStructureAPI.createEnvironment({
        name,
        category: quickCategory,
      });
      if (!created.success || !created.data) {
        showAlert({ message: created.error || "Failed to create environment", variant: "error" });
        return;
      }
      const linked = await virtualIPAPI.linkVirtualIPEnvironment(ipKey, {
        environment_id: created.data.id,
      });
      if (linked.success && linked.data) {
        refreshLinks([linked.data, ...links]);
        setEnvironments((prev) => [created.data!, ...prev]);
        setQuickName("");
        showAlert({ message: "Environment created and linked to IP", variant: "success" });
      } else {
        showAlert({ message: linked.error || "Environment created successfully, but linking failed", variant: "error" });
      }
    } finally {
      setLinking(false);
    }
  };

  const handleUnlink = async (link: VirtualIPEnvironmentLink) => {
    const res = await virtualIPAPI.unlinkVirtualIPEnvironment(ipKey, link.environment_id);
    if (res.success) {
      refreshLinks(links.filter((item) => item.id !== link.id));
      showAlert({ message: "Environment unlinked from IP", variant: "success" });
    } else {
      showAlert({ message: res.error || "Failed to remove link", variant: "error" });
    }
  };

  return (
    <OperatorPanel id="ip-environments">
      <OperatorSectionHeader
        title="Environment Assets"
        subtitle="Link reusable scenes, locations, and background image pools to this IP"
        action={<StatusPill tone={links.length ? "green" : "amber"}>{links.length} linked</StatusPill>}
      />
      <div className="space-y-4 p-4">
        {loading ? (
          <OperatorState title="Loading IP environment assets..." />
        ) : links.length ? (
          <div className="grid gap-3 md:grid-cols-2">
            {links.map((link) => (
              <div key={link.id} className="rounded-lg border border-gray-200 p-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="truncate text-sm font-semibold text-gray-950">
                      {link.environment.name}
                    </div>
                    <div className="mt-1 text-xs text-gray-500">
                      {link.environment.category || "Uncategorized"} · {link.usage_type}
                    </div>
                  </div>
                  <StatusPill tone={link.is_default ? "blue" : "gray"}>
                    {link.is_default ? "Default" : "Linked"}
                  </StatusPill>
                </div>
                {link.environment.description ? (
                  <p className="mt-2 line-clamp-2 text-xs text-gray-600">
                    {link.environment.description}
                  </p>
                ) : null}
                <div className="mt-3 flex gap-2">
                  <Link
                    href={`/environments/${link.environment.business_id || link.environment_id}`}
                    className={operatorButtonClass("secondary")}
                  >
                    Manage Images
                  </Link>
                  <button
                    type="button"
                    onClick={() => void handleUnlink(link)}
                    className={operatorButtonClass("ghost")}
                  >
                    Remove Link
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <OperatorState
            tone="amber"
            title="Environments Pending Link"
            detail="Once linked, stories, timeline, and storyboards will prioritize this IP's environment pool."
          />
        )}

        <div className="grid gap-3 border-t border-gray-100 pt-4 lg:grid-cols-2">
          <div className="flex gap-2">
            <select
              value={selectedEnvId}
              onChange={(event) => setSelectedEnvId(event.target.value)}
              className={operatorSelectClass("min-w-0 flex-1")}
            >
              <option value="">Select existing environment</option>
              {availableEnvironments.map((env) => (
                <option key={env.id} value={env.id}>
                  {env.name}
                </option>
              ))}
            </select>
            <button
              type="button"
              disabled={!selectedEnvId || linking}
              onClick={() => void handleLinkExisting()}
              className={operatorButtonClass("primary")}
            >
              Link
            </button>
          </div>
          <div className="flex gap-2">
            <input
              value={quickName}
              onChange={(event) => setQuickName(event.target.value)}
              placeholder="New environment name"
              className={operatorInputClass("min-w-0 flex-1")}
            />
            <select
              value={quickCategory}
              onChange={(event) => setQuickCategory(event.target.value)}
              className={operatorSelectClass("w-24")}
            >
              <option value="indoor">Indoor</option>
              <option value="outdoor">Outdoor</option>
              <option value="other">Other</option>
            </select>
            <button
              type="button"
              disabled={!quickName.trim() || linking}
              onClick={() => void handleQuickCreate()}
              className={operatorButtonClass("secondary")}
            >
              Create and Link
            </button>
          </div>
        </div>
      </div>
    </OperatorPanel>
  );
}
