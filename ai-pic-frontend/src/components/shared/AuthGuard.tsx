"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  buildLoginPathForReturn,
  currentBrowserReturnPath,
} from "@/utils/authReturnPath";
import { isAuthenticated } from "@/utils/auth";

interface AuthGuardProps {
  children: React.ReactNode;
}

export default function AuthGuard({ children }: AuthGuardProps) {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = () => {
      const isAuth = isAuthenticated();

      if (!isAuth) {
        router.push(buildLoginPathForReturn(currentBrowserReturnPath()));
        return;
      }

      setAuthenticated(true);
      setLoading(false);
    };

    checkAuth();
  }, [router]);

  // Show loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Checking sign-in status...</p>
        </div>
      </div>
    );
  }

  // Do not render child components when unauthenticated
  if (!authenticated) {
    return null;
  }

  // Authenticated, render child components
  return <>{children}</>;
}
