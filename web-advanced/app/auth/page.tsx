"use client";
import React, { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { getSupabaseClient } from "@/lib/supabaseClient";

export default function AuthPage() {
  const [mode, setMode] = useState<"sign-in" | "sign-up">("sign-in");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const supabase = getSupabaseClient();
  const hasSupabase = !!supabase;

  async function handleSubmit() {
    if (!hasSupabase) return alert("Demo only - set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY to enable Auth");
    if (!email || !password) return alert("Email and password required");
    if (mode === "sign-in") {
      const { error } = await supabase!.auth.signInWithPassword({ email, password });
      if (error) return alert(error.message);
      alert("Signed in");
    } else {
      const { error } = await supabase!.auth.signUp({ email, password });
      if (error) return alert(error.message);
      alert("Check your email to confirm your account");
    }
  }

  async function oauth(provider: 'google' | 'github') {
    if (!hasSupabase) return alert("Demo OAuth - configure Supabase to enable");
    const { error } = await supabase!.auth.signInWithOAuth({ provider, options: { redirectTo: window.location.origin } });
    if (error) alert(error.message);
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center">{mode === "sign-in" ? "Sign In" : "Create Account"}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid gap-2">
              <label className="text-sm font-medium">Email</label>
              <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
            </div>
            <div className="grid gap-2">
              <label className="text-sm font-medium">Password</label>
              <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
            </div>
            <Button className="w-full" onClick={handleSubmit}> 
              {mode === "sign-in" ? "Sign In" : "Sign Up"}
            </Button>

            <div className="relative py-2 text-center text-xs text-gray-500">
              <span className="bg-white px-2">or continue with</span>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <Button variant="outline" onClick={() => oauth('google')}>Google</Button>
              <Button variant="outline" onClick={() => oauth('github')}>GitHub</Button>
            </div>

            <div className="text-center text-sm text-gray-600">
              {mode === "sign-in" ? (
                <>
                  Don't have an account?{" "}
                  <button className="text-blue-600 hover:underline" onClick={() => setMode("sign-up")}>Sign up</button>
                </>
              ) : (
                <>
                  Already have an account?{" "}
                  <button className="text-blue-600 hover:underline" onClick={() => setMode("sign-in")}>Sign in</button>
                </>
              )}
            </div>

            <div className="text-center text-xs text-gray-500">
              By continuing you agree to our <Link href="#" className="underline">Terms</Link> & <Link href="#" className="underline">Privacy</Link>.
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}