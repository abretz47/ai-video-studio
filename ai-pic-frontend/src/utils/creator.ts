import { t } from "@/lib/i18n";
import type { CreatorInfo } from "@/utils/api/types";

export const resolveCreatorLabel = (creator?: CreatorInfo | null) => {
  if (!creator) return t("common.unknown", "Unknown");
  const fullName = creator.full_name?.trim();
  if (fullName) return fullName;
  if (creator.username) return creator.username;
  return `${t("common.user", "User")} ${creator.id}`;
};
