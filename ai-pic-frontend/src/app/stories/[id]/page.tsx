"use client";

import { useParams } from "next/navigation";
import { AuthGuard, OperatorShell } from "@/components/shared";
import { StoryProductionDetail } from "@/components/features/stories/StoryProductionDetail";

function StoryDetailPageContent() {
  const params = useParams();
  const storyKey = params?.id?.toString() || "";

  return (
    <OperatorShell
      title="Story Production"
      subtitle="Story details, episodes, and generation prep"
      breadcrumb={["IP Center", "Story Production", storyKey]}
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
