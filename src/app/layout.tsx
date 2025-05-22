import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import ClientLayout from "@/components/fixed-client-layout";

// Load the Inter font with specific configuration
const inter = Inter({ 
  subsets: ["latin"],
  display: 'swap',
  variable: '--font-inter',
  preload: true,
  fallback: ['system-ui', 'sans-serif']
});

export const metadata: Metadata = {
  title: "SkinPredict - AI Skin Analysis",
  description: "Get personalized skin analysis and recommendations from our AI dermatology assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className={inter.variable}>
      <body className={`font-sans ${inter.className}`} suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
