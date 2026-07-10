"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { OperatorState } from "@/components/shared";

export default function AdminPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the user management page
    router.replace("/admin/users");
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#f5f6f8]">
      <OperatorState title="Entering admin console..." />
    </div>
  );
}
