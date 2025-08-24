"use client";
import React from "react";
import { Navigation } from "@/components/layout/navigation";

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex">
        <aside className="w-64 border-r bg-white hidden md:block">
          <div className="p-4 font-bold text-lg">CamboAI</div>
          <div className="p-2">
            <Navigation />
          </div>
        </aside>
        <main className="flex-1">
          {children}
        </main>
      </div>
    </div>
  );
}