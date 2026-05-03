import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SynapSpace AG2 Beta Playground",
  description: "Live multi-agent event orchestration with AG2 beta and AG-UI"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
