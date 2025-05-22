'use client';

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { UserIcon } from "@heroicons/react/24/outline";
import Link from "next/link";
import * as React from "react";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import * as Avatar from "@radix-ui/react-avatar";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
import { logout } from "@/lib/firebase";
import type { User } from 'firebase/auth';

export function UserMenu() {
  // First, handle client-side mounting
  const [mounted, setMounted] = useState(false);
  
  // Use the auth context
  const { currentUser, loading: authLoading } = useAuth();
  
  // Mount effect - only run on client
  useEffect(() => { 
    setMounted(true);
  }, []);
  // Show loading state while mounting or loading auth
  if (!mounted || authLoading) {
    return <Button variant="ghost" size="icon" className="relative rounded-full">
      <UserIcon className="h-5 w-5" />
    </Button>;
  }  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Failed to logout:', error);
    }
  };

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <Button variant="ghost" size="icon" className="relative rounded-full">
          {currentUser && currentUser.photoURL ? (
            <Avatar.Root className="h-8 w-8 rounded-full overflow-hidden">
              <Avatar.Image 
                src={currentUser.photoURL} 
                alt={currentUser.displayName || currentUser.email || "User profile"} 
                className="h-full w-full object-cover"
              />
              <Avatar.Fallback className="flex h-full w-full items-center justify-center bg-slate-100 dark:bg-slate-800">
                {(currentUser.displayName?.charAt(0) || currentUser.email?.charAt(0) || "U").toUpperCase()}
              </Avatar.Fallback>
            </Avatar.Root>
          ) : (
            <UserIcon className="h-5 w-5" />
          )}
        </Button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          align="end"
          sideOffset={5}
          className={cn(
            "z-50 min-w-[12rem] overflow-hidden rounded-md border border-slate-200 bg-white p-1 shadow-md animate-in slide-in-from-top-2",
            "dark:border-slate-800 dark:bg-slate-950"
          )}
        >
          {currentUser ? (
            <>
              <DropdownMenu.Item className="px-2 py-1.5 text-sm text-slate-500 dark:text-slate-400">
                Signed in as <span className="font-medium">{currentUser.displayName || currentUser.email}</span>
              </DropdownMenu.Item>
              <DropdownMenu.Separator className="my-1 h-px bg-slate-200 dark:bg-slate-800" />
              <Link href="/profile" passHref>
                <DropdownMenu.Item
                  className={cn(
                    "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors",
                    "focus:bg-slate-100 focus:text-slate-900 dark:focus:bg-slate-800 dark:focus:text-slate-50"
                  )}
                >
                  Your Profile
                </DropdownMenu.Item>
              </Link>
              <DropdownMenu.Separator className="my-1 h-px bg-slate-200 dark:bg-slate-800" />
              <DropdownMenu.Item
                className={cn(
                  "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors",
                  "focus:bg-slate-100 focus:text-slate-900 dark:focus:bg-slate-800 dark:focus:text-slate-50"
                )}
                onSelect={handleLogout}
              >
                Log out
              </DropdownMenu.Item>
            </>
          ) : (
            <>
              <Link href="/login" passHref>
                <DropdownMenu.Item
                  className={cn(
                    "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors",
                    "focus:bg-slate-100 focus:text-slate-900 dark:focus:bg-slate-800 dark:focus:text-slate-50"
                  )}
                >
                  Log in
                </DropdownMenu.Item>
              </Link>
              <Link href="/signup" passHref>
                <DropdownMenu.Item
                  className={cn(
                    "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors",
                    "focus:bg-slate-100 focus:text-slate-900 dark:focus:bg-slate-800 dark:focus:text-slate-50"
                  )}
                >
                  Sign up
                </DropdownMenu.Item>
              </Link>
            </>
          )}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}
