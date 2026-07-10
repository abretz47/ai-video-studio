"use client";

import { useState } from "react";
import {
  OperatorAuthFrame,
  OperatorPanel,
  OperatorSectionHeader,
  operatorButtonClass,
} from "@/components/shared";

export default function TestAuth() {
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const testProtectedEndpoint = async (token: string) => {
    try {
      const response = await fetch("/api/v1/virtual-ips/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setResult((prev) => `${prev}\nProtected endpoint succeeded, returned ${data.data?.length || 0} items`);
      } else {
        setResult((prev) => `${prev}\nProtected endpoint failed: ${response.status}`);
      }
    } catch (error) {
      setResult((prev) => `${prev}\nProtected endpoint error: ${error}`);
    }
  };

  const testLogin = async () => {
    setLoading(true);
    setResult("Starting login test...");
    try {
      const response = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "username=admin&password=Ai7dio",
      });
      const data = await response.json();
      if (response.ok) {
        setResult(`Login succeeded. Token: ${data.access_token.substring(0, 50)}...`);
        localStorage.setItem("auth_token", data.access_token);
        await testProtectedEndpoint(data.access_token);
      } else {
        setResult(`Login failed: ${data.detail || "Unknown error"}`);
      }
    } catch (error) {
      setResult(`Request error: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const testApiClient = async () => {
    setLoading(true);
    setResult("Testing API client...");
    try {
      const { authAPI } = await import("@/utils/api/endpoints");
      const response = await authAPI.login({ email: "admin", password: "Ai7dio" });
      if (response.success && response.data) {
        setResult(
          `API client login succeeded. Token: ${response.data.access_token.substring(0, 50)}...`,
        );
      } else {
        setResult(`API client login failed: ${response.error}`);
      }
    } catch (error) {
      setResult(`API client error: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <OperatorAuthFrame
      title="Auth Diagnostics"
      subtitle="Verify the login endpoint and protected endpoints"
      switchLabel="Back"
      switchHref="/login"
      switchText="Login Page"
    >
      <OperatorPanel>
        <OperatorSectionHeader title="Diagnostics" subtitle="fetch and API client" />
        <div className="space-y-3 p-4">
          <button
            type="button"
            onClick={testLogin}
            disabled={loading}
            className={operatorButtonClass("primary", "w-full")}
          >
            {loading ? "Testing..." : "Test Direct fetch Login"}
          </button>
          <button
            type="button"
            onClick={testApiClient}
            disabled={loading}
            className={operatorButtonClass("secondary", "w-full")}
          >
            {loading ? "Testing..." : "Test API Client Login"}
          </button>
          <div className="min-h-32 rounded-md border border-gray-200 bg-gray-50 p-3">
            <h3 className="mb-2 text-xs font-semibold text-gray-500">Test Results</h3>
            <pre className="whitespace-pre-wrap text-xs text-gray-700">
              {result || "Click a button to start testing..."}
            </pre>
          </div>
        </div>
      </OperatorPanel>
    </OperatorAuthFrame>
  );
}
