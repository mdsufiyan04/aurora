import React from 'react';

export function ConsoleLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="h-screen w-screen flex flex-col bg-bridge-deep text-bridge-text overflow-hidden">
      {children}
    </div>
  );
}
