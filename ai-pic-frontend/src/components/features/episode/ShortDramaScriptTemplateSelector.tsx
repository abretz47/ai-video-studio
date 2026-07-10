"use client";

import { useMemo, useState } from "react";
import type { ScriptGenerationRequest } from "@/utils/api/types";
import { SHORT_DRAMA_SCRIPT_TEMPLATES } from "@/utils/shortDramaTemplates";

interface ShortDramaScriptTemplateSelectorProps {
  setGenerateForm: React.Dispatch<
    React.SetStateAction<ScriptGenerationRequest>
  >;
}

const buildMergedRequirements = (
  templateText: string | undefined,
  current: string | undefined,
) => {
  const next = (templateText ?? "").trim();
  const existing = (current ?? "").trim();
  if (!next) return current ?? "";
  return existing ? `${next}\n\n${existing}` : next;
};

export function ShortDramaScriptTemplateSelector({
  setGenerateForm,
}: ShortDramaScriptTemplateSelectorProps) {
  const [templateId, setTemplateId] = useState("");
  const selectedTemplate = useMemo(
    () => SHORT_DRAMA_SCRIPT_TEMPLATES.find((item) => item.id === templateId),
    [templateId],
  );

  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Short Drama Script Template (Optional)
      </label>
      <select
        value={templateId}
        onChange={(e) => {
          const value = e.target.value;
          setTemplateId(value);
          const template = SHORT_DRAMA_SCRIPT_TEMPLATES.find(
            (item) => item.id === value,
          );
          if (!template) return;
          setGenerateForm((prev) => ({
            ...prev,
            ...template.defaults,
            additional_requirements: buildMergedRequirements(
              template.defaults.additional_requirements,
              prev.additional_requirements,
            ),
          }));
        }}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">No Template</option>
        {SHORT_DRAMA_SCRIPT_TEMPLATES.map((template) => (
          <option key={template.id} value={template.id}>
            {template.label}
          </option>
        ))}
      </select>
      <p className="mt-1 text-xs text-gray-500">
        {selectedTemplate?.description ||
          "Selecting a template will automatically add short drama payoff and hook structure requirements to the additional requirements."}
      </p>
    </div>
  );
}
