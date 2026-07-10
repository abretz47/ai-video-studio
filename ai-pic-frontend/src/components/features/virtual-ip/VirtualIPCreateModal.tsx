"use client";

import {
  useCallback,
  useEffect,
  type Dispatch,
  type FormEvent,
  type SetStateAction,
} from "react";
import { locale, t } from "@/lib/i18n";
import type { VoiceConfig } from "@/utils/api/types";
import { CreationOverlay, SmartInputField } from "@/components/shared";
import type { AlertOptions } from "@/components/shared/modals/AlertModalProvider";
import { useVoiceConfigOptions } from "@/hooks/useVoiceConfigOptions";
import { useVoicePreview } from "@/hooks/useVoicePreview";
import type { VirtualIPCreateFormState } from "@/utils/virtual-ip/types";
import { VirtualIPAIIntroSection } from "./VirtualIPAIIntroSection";
import {
  VirtualIPCreateFooter,
  VirtualIPStatusSettings,
} from "./VirtualIPCreateModalParts";
import { VirtualIPTagsField } from "./VirtualIPTagsField";
import { VirtualIPVoicePreviewSection } from "./VirtualIPVoicePreviewSection";
import { VirtualIPVoiceSettingsForm } from "./VirtualIPVoiceSettingsForm";

interface VirtualIPCreateModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (
    event: FormEvent,
    previewSourceUrl?: string,
    previewText?: string,
  ) => void;
  showAlert: (options: AlertOptions) => void;
  aiBrief: string;
  setAiBrief: (value: string) => void;
  aiGenerating: boolean;
  onGenerateAI: () => void;
  formState: VirtualIPCreateFormState;
  setFormState: Dispatch<SetStateAction<VirtualIPCreateFormState>>;
  addTag: (tag: string) => void;
  removeTag: (tag: string) => void;
}

export function VirtualIPCreateModal({
  open,
  onClose,
  onSubmit,
  showAlert,
  aiBrief,
  setAiBrief,
  aiGenerating,
  onGenerateAI,
  formState,
  setFormState,
  addTag,
  removeTag,
}: VirtualIPCreateModalProps) {
  const updateField = <K extends keyof VirtualIPCreateFormState>(
    key: K,
    value: VirtualIPCreateFormState[K],
  ) => {
    setFormState((prev) => ({ ...prev, [key]: value }));
  };

  const setVoiceConfig = useCallback(
    (next: SetStateAction<VoiceConfig>) => {
      setFormState((prev) => ({
        ...prev,
        voice_config:
          typeof next === "function" ? next(prev.voice_config) : next,
      }));
    },
    [setFormState],
  );

  const {
    voiceEnums,
    voiceOptions,
    voiceLoading,
    voiceTypeFilter,
    setVoiceTypeFilter,
  } = useVoiceConfigOptions({
    voiceConfig: formState.voice_config,
    setVoiceConfig,
  });

  const defaultPreviewText = formState.name
    ? t("virtualIp.create.previewTextWithName", "Hi, I'm {name}. Nice to meet you.").replace("{name}", formState.name)
    : locale.toLowerCase().startsWith("zh")
    ? t("virtualIp.create.previewTextDefault", "Hi, I'm your virtual character. Nice to meet you.")
    : "Hi, I'm your virtual character. Nice to meet you.";
  const {
    previewText,
    setPreviewText,
    previewLoading,
    previewAudioUrl,
    previewSourceUrl,
    handlePreviewVoice,
    resetPreview,
  } = useVoicePreview({
    voiceConfig: formState.voice_config,
    setVoiceConfig,
    voiceEnums,
    voiceOptions,
    defaultText: defaultPreviewText,
    showAlert,
  });

  useEffect(() => {
    if (!open) {
      resetPreview();
    }
  }, [open, resetPreview]);

  const canPreview = Boolean(
    formState.voice_config.provider || voiceEnums?.providers?.length,
  );

  const handleSubmit = (event: FormEvent) => {
    onSubmit(event, previewSourceUrl || undefined, previewText);
  };

  return (
    <CreationOverlay
      open={open}
      title={t("virtualIp.create.title", "Create IP")}
      subtitle={t("virtualIp.create.subtitle", "Start organizing stories and episodes from character assets")}
      onClose={onClose}
      widthClassName="max-w-5xl"
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="rounded-md border border-blue-200 bg-blue-50 px-3 py-2 text-xs text-blue-700">
          {t("virtualIp.create.notice", "A new IP becomes the story production entry point and can continue into character assets and episode content.")}
        </div>

        <SmartInputField
          label={t("virtualIp.create.nameLabel", "Name *")}
          value={formState.name}
          onChange={(value) => updateField("name", value)}
          placeholder={t("virtualIp.create.namePlaceholder", "Enter a virtual IP name, for example: Xiaoya, Professor Li, Xiao Ming")}
          type="input"
          showAIAssist={false}
        />

        <VirtualIPAIIntroSection
          name={formState.name}
          aiBrief={aiBrief}
          setAiBrief={setAiBrief}
          aiGenerating={aiGenerating}
          onGenerateAI={onGenerateAI}
        />

        <SmartInputField
          label={t("virtualIp.create.descriptionLabel", "Character Description")}
          value={formState.description}
          onChange={(value) => updateField("description", value)}
          placeholder={t("virtualIp.create.descriptionPlaceholder", "Describe the character's core traits, personality, and appearance")}
          type="textarea"
          rows={3}
          aiSuggestType="description"
          contextData={{ name: formState.name }}
          showAIAssist={false}
        />

        <SmartInputField
          label={t("virtualIp.create.backgroundLabel", "Background Story")}
          value={formState.background_story}
          onChange={(value) => updateField("background_story", value)}
          placeholder={t("virtualIp.create.backgroundPlaceholder", "Describe the character's growth, major events, and life background")}
          type="textarea"
          rows={4}
          aiSuggestType="background_story"
          contextData={{
            name: formState.name,
            description: formState.description,
          }}
          showAIAssist={false}
        />

        <SmartInputField
          label={t("virtualIp.create.biographyLabel", "Biography")}
          value={formState.biography}
          onChange={(value) => updateField("biography", value)}
          placeholder={t("virtualIp.create.biographyPlaceholder", "Introduce the character's life, achievements, and major relationships")}
          type="textarea"
          rows={4}
          aiSuggestType="biography"
          contextData={{
            name: formState.name,
            description: formState.description,
            basicInfo: formState.background_story,
          }}
          showAIAssist={false}
        />

        <SmartInputField
          label={t("virtualIp.create.stylePromptLabel", "Style Prompt")}
          value={formState.style_prompt}
          onChange={(value) => updateField("style_prompt", value)}
          placeholder={t("virtualIp.create.stylePromptPlaceholder", "Style prompt for image generation (can be refined after generation)")}
          type="textarea"
          rows={4}
          showAIAssist={false}
        />

        <VirtualIPVoiceSettingsForm
          voiceEnums={voiceEnums}
          voiceTypeFilter={voiceTypeFilter}
          setVoiceTypeFilter={setVoiceTypeFilter}
          voiceSettings={formState.voice_config}
          setVoiceSettings={setVoiceConfig}
          voiceLoading={voiceLoading}
          voiceOptions={voiceOptions}
        />

        <VirtualIPVoicePreviewSection
          previewText={previewText}
          setPreviewText={setPreviewText}
          previewLoading={previewLoading}
          previewAudioUrl={previewAudioUrl}
          onPreview={handlePreviewVoice}
          canPreview={canPreview}
        />

        <VirtualIPStatusSettings
          isActive={formState.is_active}
          isPublic={formState.is_public}
          onActiveChange={(value) => updateField("is_active", value)}
          onPublicChange={(value) => updateField("is_public", value)}
        />

        <VirtualIPTagsField
          tags={formState.tags}
          addTag={addTag}
          removeTag={removeTag}
        />

        <VirtualIPCreateFooter onClose={onClose} />
      </form>
    </CreationOverlay>
  );
}
