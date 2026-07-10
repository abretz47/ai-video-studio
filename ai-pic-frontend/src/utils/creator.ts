import type { CreatorInfo } from "@/utils/api/types";

export const resolveCreatorLabel = (creator?: CreatorInfo | null) => {
  if (!creator) return "Unknown";
  const fullName = creator.full_name?.trim();
  if (fullName) return fullName;
  if (creator.username) return creator.username;
  return `User ${creator.id}`;
};
