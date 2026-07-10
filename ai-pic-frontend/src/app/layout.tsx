import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AlertModalProvider } from "@/components/shared/modals";
import { ToastProvider } from "@/components/shared/notifications";
import { locale, t } from "@/lib/i18n";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: t("app.layout.title", "AI Video Studio"),
  description: t(
    "app.layout.description",
    "AI-powered short drama production platform",
  ),
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang={locale}>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <AlertModalProvider>
          <ToastProvider>{children}</ToastProvider>
        </AlertModalProvider>
      </body>
    </html>
  );
}
