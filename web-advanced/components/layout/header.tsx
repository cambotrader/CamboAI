"use client";
import React from "react";
import Link from "next/link";
import { useSession, signIn, signOut } from "next-auth/react";
import { Button } from "@/components/ui/button";

export function Header() {
  const { data: session, status } = useSession();
  const loading = status === "loading";

  return (
    <header className="w-full border-b bg-white/60 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/" className="font-semibold">CamboAI</Link>
          <nav className="hidden md:flex items-center gap-3 text-sm text-gray-600">
            <Link href="/dashboard" className="hover:text-gray-900">Dashboard</Link>
            <Link href="/dashboard/charts" className="hover:text-gray-900">Charts</Link>
          </nav>
        </div>
        <div className="flex items-center gap-3">
          {loading ? (
            <span className="text-sm text-gray-500">Loading...</span>
          ) : session ? (
            <>
              <span className="text-sm text-gray-700">{session.user?.email || session.user?.name}</span>
              <Button size="sm" variant="outline" onClick={() => signOut({ callbackUrl: "/" })}>Logout</Button>
            </>
          ) : (
            <>
              <Button size="sm" variant="outline" asChild>
                <Link href="/auth">Sign in</Link>
              </Button>
              <Button size="sm" onClick={() => signIn()}>Login</Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}