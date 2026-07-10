"use client";

import type { VoiceConfig, VoiceEnums } from "@/utils/api/types";

interface VoiceSettingsPanelProps {
  editing: boolean;
  voiceEnums: VoiceEnums | null;
  voiceTypeFilter: string;
  setVoiceTypeFilter: (filter: string) => void;
  voiceSettings: VoiceConfig;
  setVoiceSettings: React.Dispatch<React.SetStateAction<VoiceConfig>>;
  voicePreviewText: string;
  setVoicePreviewText: (text: string) => void;
  voiceLoading: boolean;
  previewLoading: boolean;
  previewAudioUrl: string | null;
  voiceOptions: { value: string; label: string }[];
  onPreviewVoice: () => void;
}

export function VoiceSettingsPanel({
  editing,
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
  onPreviewVoice,
}: VoiceSettingsPanelProps) {
  return (
    <div className="space-y-5 border-b border-gray-100 p-5">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-950">Voice Settings</h3>
          <p className="text-sm text-gray-500">
            Bind a character voice by “Provider → Model → Voice”
          </p>
        </div>
        {!voiceEnums && (
          <span className="text-sm text-gray-500">Loading voice options...</span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Provider
          </label>
          <select
            value={voiceSettings.provider || ""}
            onChange={(e) => {
              const value = e.target.value || undefined;
              const defaultModel =
                voiceEnums?.defaults?.tts_model ||
                voiceEnums?.tts_models?.[0]?.value;
              setVoiceSettings((prev) => ({
                ...prev,
                provider: value,
                model: prev.model ?? defaultModel,
                voice_id: undefined,
              }));
            }}
            disabled={!editing}
            className="h-8 w-full rounded-md border border-gray-200 bg-white px-2 text-xs focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          >
            {(voiceEnums?.providers || []).map((p) => (
              <option key={p.value} value={p.value}>
                {p.label_zh || p.label_en}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Voice Model
          </label>
          <select
            value={voiceSettings.model || ""}
            onChange={(e) =>
              setVoiceSettings((prev) => ({
                ...prev,
                model: e.target.value || undefined,
              }))
            }
            disabled={!editing}
            className="h-8 w-full rounded-md border border-gray-200 bg-white px-2 text-xs focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          >
            {(voiceEnums?.tts_models || []).map((m) => (
              <option key={m.value} value={m.value}>
                {m.label_zh || m.label_en}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Voice Type
          </label>
          <select
            value={voiceTypeFilter}
            onChange={(e) => setVoiceTypeFilter(e.target.value)}
            disabled={!editing}
            className="h-8 w-full rounded-md border border-gray-200 bg-white px-2 text-xs focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
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
            disabled={!editing || voiceLoading}
            className="h-8 w-full rounded-md border border-gray-200 bg-white px-2 text-xs focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          >
            <option value="">Select a voice</option>
            {voiceOptions.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-gray-500">
            Source: {voiceSettings.provider || "Default"} /{" "}
            {voiceSettings.model || "Not selected"}
          </p>
        </div>
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Preview Text
        </label>
        <textarea
          value={voicePreviewText}
          onChange={(e) => setVoicePreviewText(e.target.value)}
          rows={3}
          className="w-full rounded-md border border-gray-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          placeholder="Enter text for the voice preview"
        />
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onPreviewVoice}
            disabled={previewLoading}
            className="h-8 rounded-md bg-blue-600 px-3 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-60"
          >
            {previewLoading ? "Generating..." : "Preview"}
          </button>
          {previewAudioUrl && (
            <audio controls src={previewAudioUrl} className="w-full max-w-md">
              Your browser does not support audio playback.
            </audio>
          )}
        </div>
        <p className="text-sm text-gray-500">
          After saving, this voice will be linked to the current character.
        </p>
      </div>
    </div>
  );
}
