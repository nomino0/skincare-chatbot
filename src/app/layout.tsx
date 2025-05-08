import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

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
    <html lang="en">
      <body className={inter.className}>
        <main className="min-h-screen">
          {children}
        </main>
        <footer className="bg-gray-100 py-6 mt-12">
          <div className="container mx-auto px-4 text-center text-gray-600 text-sm">
            <p>&copy; {new Date().getFullYear()} SkinPredict. All rights reserved.</p>
            <p className="mt-2">
              This is a demonstration project. Skin analysis results should not replace professional medical advice.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
