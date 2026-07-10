"use client";

import type { VoiceConfig, VoiceEnums } from "@/utils/api/types";

interface VirtualIPVoiceSettingsFormProps {
  voiceEnums: VoiceEnums | null;
  voiceTypeFilter: string;
  setVoiceTypeFilter: (value: string) => void;
  voiceSettings: VoiceConfig;
  setVoiceSettings: React.Dispatch<React.SetStateAction<VoiceConfig>>;
  voiceLoading: boolean;
  voiceOptions: { value: string; label: string }[];
}

export function VirtualIPVoiceSettingsForm({
  voiceEnums,
  voiceTypeFilter,
  setVoiceTypeFilter,
  voiceSettings,
  setVoiceSettings,
  voiceLoading,
  voiceOptions,
}: VirtualIPVoiceSettingsFormProps) {
  const hasProvider = Boolean(voiceSettings.provider);

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-sm font-medium text-gray-900">
            Voice settings (optional)
          </h3>
          <p className="text-xs text-gray-500">
            Bind character voice settings in the order “Provider → Model → Voice”
          </p>
        </div>
        {!voiceEnums && (
          <span className="text-xs text-gray-500">Loading voice options...</span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Provider
          </label>
          <select
            value={voiceSettings.provider || ""}
            onChange={(e) => {
              const value = e.target.value || undefined;
              if (!value) {
                setVoiceSettings({});
                return;
              }
              const defaultModel =
                voiceEnums?.defaults?.tts_model ||
                voiceEnums?.tts_models?.[0]?.value;
              setVoiceSettings((prev) => ({
                ...prev,
                provider: value,
                model: prev.model ?? defaultModel,
                voice_type: prev.voice_type ?? voiceTypeFilter,
                voice_id: undefined,
              }));
            }}
            className="h-8 w-full rounded-md border border-gray-200 bg-white px-2 text-xs focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          >
            <option value="">Do not configure for now</option>
            {(voiceEnums?.providers || []).map((p) => (
              <option key={p.value} value={p.value}>
                {p.label_zh || p.label_en}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Voice model
          </label>
          <select
            value={voiceSettings.model || ""}
            onChange={(e) =>
              setVoiceSettings((prev) => ({
                ...prev,
                model: e.target.value || undefined,
              }))
            }
            disabled={!hasProvider}
            className="h-8 w-full rounded-md border border-gray-200 bg-white px-2 text-xs focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100 disabled:bg-gray-50"
          >
            <option value="">Select a model</option>
            {(voiceEnums?.tts_models || []).map((m) => (
              <option key={m.value} value={m.value}>
                {m.label_zh || m.label_en}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Voice type
          </label>
          <select
            value={voiceTypeFilter}
            onChange={(e) => setVoiceTypeFilter(e.target.value)}
            disabled={!hasProvider}
            className="h-8 w-full rounded-md border border-gray-200 bg-white px-2 text-xs focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100 disabled:bg-gray-50"
          >
            {(voiceEnums?.voice_types || []).map((item) => (
              <option key={item.value} value={item.value}>
                {item.label_zh || item.label_en}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center justify-between">
            Voice
            {voiceLoading && (
              <span className="text-xs text-gray-500">Loading...</span>
            )}
          </label>
          <select
            value={voiceSettings.voice_id || ""}
            onChange={(e) =>
              setVoiceSettings((prev) => ({
                ...prev,
                voice_id: e.target.value || undefined,
              }))
            }
            disabled={!hasProvider || voiceLoading}
            className="h-8 w-full rounded-md border border-gray-200 bg-white px-2 text-xs focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100 disabled:bg-gray-50"
          >
            <option value="">Select a voice</option>
            {voiceOptions.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-gray-500">
            Source: {voiceSettings.provider || "Not selected"} /{" "}
            {voiceSettings.model || "Not selected"}
          </p>
        </div>
      </div>
    </div>
  );
}
