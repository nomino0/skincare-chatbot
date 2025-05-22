'use client';
import React from 'react';
import { Navbar } from './ui/navbar';

// Force re-export to ensure newest version is used
export { UserMenu } from './ui/user-menu';

export default function NavbarWrapper() {
  const [mounted, setMounted] = React.useState(false);
  
  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <div className="h-16"></div>; // Placeholder with same height as navbar
  }

  return <Navbar />;
}
