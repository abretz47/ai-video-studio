"use client";

import { operatorButtonClass } from "@/components/shared";
import type { UploadFormState } from "@/hooks/useVirtualIPImages";

interface ImageUploadFormProps {
  uploadForm: UploadFormState;
  setUploadForm: React.Dispatch<React.SetStateAction<UploadFormState>>;
  uploading: boolean;
  onUpload: () => void;
}

export function ImageUploadForm({
  uploadForm,
  setUploadForm,
  uploading,
  onUpload,
}: ImageUploadFormProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-gray-950">Upload Images</h3>
      <div className="grid grid-cols-1 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Choose Files
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) =>
              setUploadForm((prev) => ({
                ...prev,
                file: e.target.files?.[0] || null,
              }))
            }
            className="w-full rounded-md border border-gray-200 px-3 py-2 text-sm focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Image Category
          </label>
          <select
            value={uploadForm.category}
            onChange={(e) =>
              setUploadForm((prev) => ({
                ...prev,
                category: e.target.value,
              }))
            }
            className="h-8 w-full rounded-md border border-gray-200 bg-white px-2 text-xs focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          >
            <option value="portrait">Portrait</option>
            <option value="full_body">Full Body</option>
            <option value="scene">Scene</option>
            <option value="action">Action</option>
            <option value="emotion">Emotion</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tags (optional, comma separated)
          </label>
          <input
            type="text"
            value={uploadForm.tags}
            onChange={(e) =>
              setUploadForm((prev) => ({ ...prev, tags: e.target.value }))
            }
            placeholder="For example: smiling, sunny, outdoors"
            className="h-8 w-full rounded-md border border-gray-200 px-3 text-xs focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          />
        </div>
        <div className="flex items-center">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={uploadForm.is_default}
              onChange={(e) =>
                setUploadForm((prev) => ({
                  ...prev,
                  is_default: e.target.checked,
                }))
              }
              className="mr-2"
            />
            <span className="text-sm text-gray-700">Set as Default Image</span>
          </label>
        </div>
      </div>
      <div className="mt-4">
        <button
          onClick={onUpload}
          disabled={uploading || !uploadForm.file}
          className={operatorButtonClass("primary")}
        >
          {uploading ? "Uploading..." : "Upload Images"}
        </button>
      </div>
    </div>
  );
}
