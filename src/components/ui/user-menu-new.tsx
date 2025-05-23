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
import type { User } from 'firebase/auth';

export function UserMenu() {
  // First, handle client-side mounting
  const [mounted, setMounted] = useState(false);
  
  // Use the auth context hook
  const { currentUser, loading: authLoading } = useAuth();
  
  // Mount effect
  useEffect(() => { 
    setMounted(true);
  }, []);

  // Show loading state while mounting or loading auth
  if (!mounted || authLoading) {
    return <Button variant="ghost" size="icon" className="relative rounded-full">
      <UserIcon className="h-5 w-5" />
    </Button>;
  }

  const handleLogout = async () => {
    try {
      const { logout } = await import('@/lib/firebase');
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
            "z-50 min-w-[12rem] overflow-hidden rounded-md border border-border bg-card p-1 shadow-md animate-in slide-in-from-top-2 data-[side=bottom]:slide-in-from-top-2 data-[side=top]:slide-in-from-bottom-2",
          )}
        >
          {currentUser ? (
            <>
              <DropdownMenu.Item className="px-2 py-1.5 text-sm text-muted-foreground">
                Signed in as <span className="font-medium">{currentUser.displayName || currentUser.email}</span>
              </DropdownMenu.Item>
              <DropdownMenu.Separator className="my-1 h-px bg-border" />
              <Link href="/profile" passHref>
                <DropdownMenu.Item
                  className={cn(
                    "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors",
                    "focus:bg-accent focus:text-accent-foreground"
                  )}
                >
                  Your Profile
                </DropdownMenu.Item>
              </Link>
              <DropdownMenu.Separator className="my-1 h-px bg-border" />
              <DropdownMenu.Item
                className={cn(
                  "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors",
                  "focus:bg-accent focus:text-accent-foreground"
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
                    "focus:bg-accent focus:text-accent-foreground"
                  )}
                >
                  Log in
                </DropdownMenu.Item>
              </Link>
              <Link href="/signup" passHref>
                <DropdownMenu.Item
                  className={cn(
                    "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors",
                    "focus:bg-accent focus:text-accent-foreground"
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
