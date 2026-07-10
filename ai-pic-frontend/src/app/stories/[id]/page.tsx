"use client";

import { useParams } from "next/navigation";
import { t } from "@/lib/i18n";
import { AuthGuard, OperatorShell } from "@/components/shared";
import { StoryProductionDetail } from "@/components/features/stories/StoryProductionDetail";

function StoryDetailPageContent() {
  const params = useParams();
  const storyKey = params?.id?.toString() || "";

  return (
    <OperatorShell
      title={t("stories.detail.pageTitle", "Story Production")}
      subtitle={t("stories.detail.pageSubtitle", "Story details, episodes, and generation preparation")}
      breadcrumb={[
        t("common.breadcrumb.ipCenter", "IP Center"),
        t("stories.board.breadcrumb", "Story Production"),
        storyKey,
      ]}
    >
      <StoryProductionDetail storyKey={storyKey} />
    </OperatorShell>
  );
}

export default function StoryDetailPage() {
  return (
    <AuthGuard>
      <StoryDetailPageContent />
    </AuthGuard>
  );
}
