"use client";

import { t } from "@/lib/i18n";

interface VirtualIPVoicePreviewSectionProps {
  previewText: string;
  setPreviewText: (text: string) => void;
  previewLoading: boolean;
  previewAudioUrl: string | null;
  onPreview: () => void;
  canPreview: boolean;
}

export function VirtualIPVoicePreviewSection({
  previewText,
  setPreviewText,
  previewLoading,
  previewAudioUrl,
  onPreview,
  canPreview,
}: VirtualIPVoicePreviewSectionProps) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {t("virtualIp.voice.previewText", "Preview text")}
      </label>
      <textarea
        value={previewText}
        onChange={(e) => setPreviewText(e.target.value)}
        rows={3}
        className="w-full rounded-md border border-gray-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
        placeholder={t("virtualIp.voice.previewPlaceholder", "Enter text to preview the voice")}
      />
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onPreview}
          disabled={!canPreview || previewLoading}
          className="h-8 rounded-md bg-blue-600 px-3 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-60"
        >
          {previewLoading ? t("common.generating", "Generating...") : t("virtualIp.voice.preview", "Preview")}
        </button>
        {previewAudioUrl && (
          <audio controls src={previewAudioUrl} className="w-full max-w-md">
            {t("virtualIp.voice.audioUnsupported", "Your browser does not support audio playback.")}
          </audio>
        )}
      </div>
      {!canPreview && (
        <p className="text-xs text-gray-500">
          {t("virtualIp.voice.previewDisabled", "Select a provider and voice model before previewing.")}
        </p>
      )}
      <p className="text-xs text-gray-500">
        {t("virtualIp.voice.previewSaveHint", "After saving, the preview will be uploaded to OSS automatically and bound to this character.")}
      </p>
    </div>
  );
}
