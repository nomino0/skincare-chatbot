'use client';

import { useAuth } from "@/lib/auth-context";
import { useRouter, usePathname } from "next/navigation";
import { useEffect } from "react";
import { LoadingScreen } from "@/components/ui/loading";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { currentUser, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !currentUser) {
      // Save the current path to redirect back after login
      localStorage.setItem('redirectAfterLogin', pathname);
      router.push('/login');
    }
  }, [currentUser, loading, router, pathname]);

  if (loading) {
    return <LoadingScreen />;
  }

  if (!currentUser) {
    return null;
  }

  return <>{children}</>;
}
