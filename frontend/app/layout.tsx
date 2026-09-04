import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Meal Planner",
  description: "Personalized Indian meal plans for real daily life.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
