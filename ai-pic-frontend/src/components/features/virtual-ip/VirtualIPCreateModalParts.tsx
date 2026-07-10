"use client";

import { operatorButtonClass } from "@/components/shared";

interface StatusSettingsProps {
  isActive: boolean;
  isPublic: boolean;
  onActiveChange: (value: boolean) => void;
  onPublicChange: (value: boolean) => void;
}

export function VirtualIPStatusSettings({
  isActive,
  isPublic,
  onActiveChange,
  onPublicChange,
}: StatusSettingsProps) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-gray-700">
        Status settings
      </label>
      <div className="flex flex-col gap-3 rounded-md border border-gray-200 bg-gray-50 p-3 sm:flex-row">
        <label className="inline-flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={isActive}
            onChange={(event) => onActiveChange(event.target.checked)}
            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          Enable character
        </label>
        <label className="inline-flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={isPublic}
            onChange={(event) => onPublicChange(event.target.checked)}
            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          Publicly visible
        </label>
      </div>
    </div>
  );
}

export function VirtualIPCreateFooter({ onClose }: { onClose: () => void }) {
  return (
    <div className="flex justify-end gap-3 border-t pt-4">
      <button
        type="button"
        onClick={onClose}
        className={operatorButtonClass("secondary")}
      >
        Cancel
      </button>
      <button type="submit" className={operatorButtonClass("primary")}>
        Create IP
      </button>
    </div>
  );
}
