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

type RegisterForm = {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
};

const fields: Array<{
  name: keyof RegisterForm;
  label: string;
  type: string;
  autoComplete: string;
  placeholder: string;
}> = [
  { name: "username", label: "Username", type: "text", autoComplete: "username", placeholder: "Enter username" },
  { name: "email", label: "Email Address", type: "email", autoComplete: "email", placeholder: "Enter email address" },
  { name: "password", label: "Password", type: "password", autoComplete: "new-password", placeholder: "At least 6 characters" },
  { name: "confirmPassword", label: "Confirm Password", type: "password", autoComplete: "new-password", placeholder: "Enter password again" },
];

export default function Register() {
  const router = useRouter();
  const [formData, setFormData] = useState<RegisterForm>({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Partial<Record<keyof RegisterForm, string>>>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [serverSuccess, setServerSuccess] = useState<string | null>(null);

  const validateForm = () => {
    const next: Partial<Record<keyof RegisterForm, string>> = {};
    if (!formData.username.trim()) next.username = "Username is required";
    if (!formData.email.trim()) next.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(formData.email)) next.email = "Invalid email format";
    if (formData.password.length < 6) next.password = "Password must be at least 6 characters";
    if (formData.password !== formData.confirmPassword) {
      next.confirmPassword = "Passwords do not match";
    }
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!validateForm()) return;
    setIsLoading(true);
    setServerError(null);
    try {
      const res = await authAPI.register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.username,
      });
      if (res.success) {
        setServerSuccess("Registration successful. Redirecting to login...");
        router.push("/login?registered=1");
      } else {
        setServerError(res.message || "Registration failed. Please try again later");
      }
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Registration failed. Please try again later");
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const name = event.target.name as keyof RegisterForm;
    setFormData((prev) => ({ ...prev, [name]: event.target.value }));
    setErrors((prev) => ({ ...prev, [name]: undefined }));
  };

  return (
    <OperatorAuthFrame
      title="Create Operator Account"
      subtitle="Register to enter the unified Virtual IP hub workspace"
      switchLabel="Already have an account?"
      switchHref="/login"
      switchText="Sign in"
    >
      <form className="space-y-4" onSubmit={handleSubmit}>
        {serverError ? <OperatorState title={serverError} tone="red" /> : null}
        {serverSuccess ? <OperatorState title={serverSuccess} tone="green" /> : null}
        {fields.map((field) => (
          <label key={field.name} className="block text-xs font-medium text-gray-600">
            {field.label}
            <input
              id={field.name}
              name={field.name}
              type={field.type}
              autoComplete={field.autoComplete}
              required
              className={operatorInputClass("mt-1 w-full")}
              placeholder={field.placeholder}
              value={formData[field.name]}
              onChange={handleChange}
            />
            {errors[field.name] ? (
              <span className="mt-1 block text-xs text-red-600">
                {errors[field.name]}
              </span>
            ) : null}
          </label>
        ))}
        <button
          type="submit"
          disabled={isLoading}
          className={operatorButtonClass("primary", "w-full")}
        >
          {isLoading ? "Registering..." : "Register"}
        </button>
      </form>
    </OperatorAuthFrame>
  );
}
