import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/AuthContext";

export const metadata: Metadata = {
  title: "CrystaGraph — AI-Driven Materials Knowledge Mining Platform",
  description:
    "Public research platform for extracting, standardizing, and synthesizing material compositions and physical properties from scientific tables and literature.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased selection:bg-sky-100 selection:text-sky-900">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
