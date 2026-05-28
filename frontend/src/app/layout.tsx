import type { Metadata } from "next";
import { Sora, Inter } from "next/font/google";
import "./globals.css";

const sora = Sora({
  subsets: ["latin"],
  variable: "--font-sora",
  weight: ["400", "600", "700", "800"],
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["300", "400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Global Opportunity Tracker — Aetheric",
  description: "AI-powered global opportunity discoverer and tracker system.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full bg-[#0f1118]">
      <body className={`${sora.variable} ${inter.variable} min-h-full flex flex-col font-sans text-gray-200 antialiased`}>
        {children}
      </body>
    </html>
  );
}
