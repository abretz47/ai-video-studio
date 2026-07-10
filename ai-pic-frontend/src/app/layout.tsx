import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import "./globals.css";
import { AlertModalProvider } from "@/components/shared/modals";
import { ToastProvider } from "@/components/shared/notifications";
import { locale, t } from "@/lib/i18n";

const geistSans = GeistSans;
const geistMono = GeistMono;

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
