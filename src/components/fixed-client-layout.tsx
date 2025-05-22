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
  
  if (!mounted) {
    // Return a minimal layout as a placeholder during server rendering
    return (
      <div className="min-h-screen bg-background">
        <div className="h-16 border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950"></div>
        <main className="container mx-auto px-4 pt-8 pb-16 min-h-[calc(100vh-4rem-8rem)]">{children}</main>
        <div className="h-32 bg-slate-100 dark:bg-slate-900"></div>
      </div>
    );
  }
  
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <div className="flex min-h-screen flex-col">
        <NavbarWrapper />
        <main className="flex-1 container mx-auto px-4 pt-8 pb-16">
          {children}
        </main>
        <footer className="bg-slate-100 py-6 dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
          <div className="container mx-auto px-4 text-center text-slate-600 text-sm dark:text-slate-400">
            <p>&copy; {new Date().getFullYear()} SkinPredict. All rights reserved.</p>
            <p className="mt-2">
              This is a demonstration project. Skin analysis results should not replace professional medical advice.
            </p>
          </div>
        </footer>
      </div>
    </ThemeProvider>
  );
}
