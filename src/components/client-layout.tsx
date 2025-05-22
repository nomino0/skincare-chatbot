'use client';

import { ThemeProvider } from "@/components/theme-provider";
import NavbarWrapper from "@/components/navbar-wrapper";
import React, { useState, useEffect } from "react";

interface ClientLayoutProps {
  children: React.ReactNode;
}

export default function ClientLayout({ children }: ClientLayoutProps) {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <NavbarWrapper />
      <main className="min-h-screen">
        {children}
      </main>
      <footer className="bg-slate-100 py-6 mt-12 dark:bg-slate-900">
        <div className="container mx-auto px-4 text-center text-slate-600 text-sm dark:text-slate-400">
          <p>&copy; {new Date().getFullYear()} SkinPredict. All rights reserved.</p>
          <p className="mt-2">
            This is a demonstration project. Skin analysis results should not replace professional medical advice.
          </p>
        </div>
      </footer>
    </ThemeProvider>
  );
}
