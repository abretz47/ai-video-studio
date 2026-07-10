"use client";

import type { ChangeEvent, FormEvent } from "react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  OperatorAuthFrame,
  OperatorState,
  operatorButtonClass,
  operatorInputClass,
} from "@/components/shared";
import { authAPI } from "@/utils/api/endpoints";
import { resolveSafeLoginReturnPath } from "@/utils/authReturnPath";

export default function Login() {
  const router = useRouter();
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setIsLoading(true);
    setError("");
    try {
      const response = await authAPI.login({
        email: formData.username,
        password: formData.password,
      });
      if (!response.success || !response.data) {
        throw new Error(response.error || "LoginFailed");
      }
      localStorage.setItem("auth_token", response.data.access_token);
      localStorage.setItem(
        "user_info",
        JSON.stringify({
          username: formData.username,
          token: response.data.access_token,
        }),
      );
      router.push(
        resolveSafeLoginReturnPath(
          new URLSearchParams(window.location.search).get("next"),
        ),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed. Please retry later");
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [event.target.name]: event.target.value,
    }));
  };

  return (
    <OperatorAuthFrame
      title="Log in to the Studio"
      subtitle="Use your account to enter the IP Center production workflow"
      switchLabel="No account yet?"
      switchHref="/register"
      switchText="Register a New Account"
    >
      <form className="space-y-4" onSubmit={handleSubmit}>
        {error ? <OperatorState title={error} tone="red" /> : null}
        <label className="block text-xs font-medium text-gray-600">
          Username
          <input
            id="username"
            name="username"
            type="text"
            autoComplete="username"
            required
            className={operatorInputClass("mt-1 w-full")}
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
          />
        </label>
        <label className="block text-xs font-medium text-gray-600">
          Password
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
            className={operatorInputClass("mt-1 w-full")}
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
          />
        </label>
        <button
          type="submit"
          disabled={isLoading}
          className={operatorButtonClass("primary", "w-full")}
        >
          {isLoading ? "LoginMedium..." : "Login"}
        </button>
      </form>
    </OperatorAuthFrame>
  );
}
