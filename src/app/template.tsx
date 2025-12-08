'use client';

import ClientLayout from "@/components/fixed-client-layout";
import { AuthProvider } from "@/lib/auth-context";
import BackendHealthGuard from "@/components/BackendHealthGuard";

export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <BackendHealthGuard>
      <AuthProvider>
        <ClientLayout>
          {children}
        </ClientLayout>
      </AuthProvider>
    </BackendHealthGuard>
  );
}
