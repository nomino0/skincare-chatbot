'use client';

import ClientLayout from "@/components/fixed-client-layout";
import { AuthProvider } from "@/lib/auth-context";

export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <ClientLayout>
        {children}
      </ClientLayout>
    </AuthProvider>
  );
}
