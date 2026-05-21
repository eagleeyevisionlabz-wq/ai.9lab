import type { Metadata } from "next";
import "./globals.css";
import { LeftRail } from "@/components/shell/LeftRail";
import { TopBar } from "@/components/shell/TopBar";

export const metadata: Metadata = {
  title: "M3ta-0S — Mission Control",
  description:
    "Sovereign AI operating system. Hermes + Obsidian + Aion + Paperclip + Claude Code, unified.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-bg text-text antialiased">
        <div className="grid min-h-screen grid-cols-[260px_1fr]">
          <LeftRail />
          <div className="flex min-h-screen flex-col">
            <TopBar />
            <main className="grid-bg flex-1 px-6 py-6">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
