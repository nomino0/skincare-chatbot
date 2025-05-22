'use client';

import React from 'react';

export function LoadingSpinner({ size = 'md', className = '' }: { size?: 'sm' | 'md' | 'lg', className?: string }) {
  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-2',
    lg: 'h-12 w-12 border-3'
  };

  return (
    <div className={`${sizeClasses[size]} animate-spin rounded-full border-t-transparent border-primary ${className}`}></div>
  );
}

export function LoadingScreen({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center">
      <LoadingSpinner size="lg" className="mb-4" />
      <p className="text-slate-600 dark:text-slate-400">{message}</p>
    </div>
  );
}
