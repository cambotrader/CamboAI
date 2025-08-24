"use client";
import React, { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function AuthPage() {
  const [mode, setMode] = useState<"sign-in" | "sign-up">("sign-in");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

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
            <Button className="w-full" onClick={() => alert("Demo only - hook up your auth here")}> 
              {mode === "sign-in" ? "Sign In" : "Sign Up"}
            </Button>

            <div className="relative py-2 text-center text-xs text-gray-500">
              <span className="bg-white px-2">or continue with</span>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <Button variant="outline" onClick={() => alert("Demo OAuth (Google)")}>Google</Button>
              <Button variant="outline" onClick={() => alert("Demo OAuth (GitHub)")}>GitHub</Button>
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