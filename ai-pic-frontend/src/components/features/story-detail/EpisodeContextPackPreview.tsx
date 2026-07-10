"use client";

export interface EpisodeContextPackPreviewProps {
  includeContinuityLedger: boolean;
  setIncludeContinuityLedger: (value: boolean) => void;
  includeCharacterCards: boolean;
  setIncludeCharacterCards: (value: boolean) => void;
  recentEpisodesCount: number;
  setRecentEpisodesCount: (value: number) => void;
  contextPackPreview: string;
  contextPackLoading: boolean;
  contextPackError: string;
  onPreviewContextPack: () => void;
}

export function EpisodeContextPackPreview({
  includeContinuityLedger,
  setIncludeContinuityLedger,
  includeCharacterCards,
  setIncludeCharacterCards,
  recentEpisodesCount,
  setRecentEpisodesCount,
  contextPackPreview,
  contextPackLoading,
  contextPackError,
  onPreviewContextPack,
}: EpisodeContextPackPreviewProps) {
  return (
    <details className="mt-4 rounded border bg-gray-50 p-3">
      <summary className="cursor-pointer text-sm font-medium text-gray-800">
        Context Preview (Context Pack)
      </summary>
      <div className="mt-3 space-y-3">
        <p className="text-xs text-gray-500">
          Review the context that will be injected for this generation
          (preview does not call the model).
        </p>

        <div className="flex flex-wrap items-center gap-4">
          <label className="text-sm text-gray-700 flex items-center gap-2">
            <input
              type="checkbox"
              checked={includeContinuityLedger}
              onChange={(e) => setIncludeContinuityLedger(e.target.checked)}
            />
            continuity ledger
          </label>
          <label className="text-sm text-gray-700 flex items-center gap-2">
            <input
              type="checkbox"
              checked={includeCharacterCards}
              onChange={(e) => setIncludeCharacterCards(e.target.checked)}
            />
            Character Cards
          </label>
          <label className="text-sm text-gray-700 flex items-center gap-2">
            Recent Summaries
            <input
              type="number"
              min={0}
              max={50}
              value={recentEpisodesCount}
              onChange={(e) =>
                setRecentEpisodesCount(
                  Math.max(0, parseInt(e.target.value) || 0),
                )
              }
              className="w-20 px-2 py-1 border rounded bg-white"
            />
            episodes
          </label>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={onPreviewContextPack}
            disabled={contextPackLoading}
            className="bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700 disabled:opacity-60"
          >
            {contextPackLoading ? "Loading..." : "Preview Context"}
          </button>
          {contextPackError ? (
            <span className="text-sm text-red-600">{contextPackError}</span>
          ) : null}
        </div>

        {contextPackPreview ? (
          <pre className="max-h-96 overflow-auto whitespace-pre-wrap break-words rounded bg-white p-3 text-xs text-gray-800 border">
            {contextPackPreview}
          </pre>
        ) : null}
      </div>
    </details>
  );
}
