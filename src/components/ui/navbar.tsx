'use client';

import Link from "next/link";
import { ThemeToggle } from "@/components/ui/theme-toggle";
// Import the user menu
import { UserMenu } from "@/components/ui/user-menu";
import { BeakerIcon } from "@heroicons/react/24/outline";
import { useAuth } from "@/lib/auth-context";

export function Navbar() {
  const { userRole } = useAuth();

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/80 backdrop-blur-sm dark:border-slate-800 dark:bg-slate-950/80">
      <div className="container mx-auto flex h-16 items-center px-4 md:px-6">
        <div className="flex gap-6 md:gap-10 flex-1">
          <Link 
            href={userRole === 'admin' ? "/admin" : userRole === 'professional' ? "/professional" : "/"} 
            className="flex items-center space-x-2"
          >
            <BeakerIcon className="h-6 w-6 text-primary" />
            <span className="inline-block font-bold text-xl hidden md:inline-block">SkinPredict</span>
          </Link>
          
          <nav className="hidden md:flex items-center gap-6 text-sm">
            {userRole === 'admin' ? (
              <Link href="/admin" className="transition-colors hover:text-primary font-medium">
                Admin Portal
              </Link>
            ) : userRole === 'professional' ? (
              <Link href="/professional" className="transition-colors hover:text-primary font-medium">
                Professional Portal
              </Link>
            ) : (
              <>
                <Link href="/" className="transition-colors hover:text-primary">
                  Home
                </Link>
                <Link href="/profile" className="transition-colors hover:text-primary">
                  Dashboard
                </Link>
                <Link href="#" className="transition-colors hover:text-primary">
                  About
                </Link>
              </>
            )}
          </nav>
        </div>
        
        <div className="flex items-center justify-end space-x-4">
          <nav className="flex items-center space-x-2">
            <ThemeToggle />
            <UserMenu />
          </nav>
        </div>
      </div>
    </header>
  );
}
