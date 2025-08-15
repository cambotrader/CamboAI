"use client";
import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

export default function SignInPage() {
  const supabase = createClient();
  const router = useRouter();
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const handleEmail = async (e: React.FormEvent) => {
    e.preventDefault(); setLoading(true); setError(null);
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    setLoading(false);
    if (error) setError(error.message); else router.replace("/");
  };

  const handleGoogle = async () => {
    setLoading(true); setError(null);
    const { error } = await supabase.auth.signInWithOAuth({ provider: "google", options: { redirectTo: typeof window !== 'undefined' ? `${window.location.origin}/` : undefined } });
    if (error) { setError(error.message); setLoading(false); }
  };

  return (
    <main className="p-6 max-w-md mx-auto">
      <h1 className="text-xl font-semibold mb-4">Sign in</h1>
      <form onSubmit={handleEmail} className="space-y-3">
        <input className="w-full border rounded px-3 py-2" type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required />
        <input className="w-full border rounded px-3 py-2" type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} required />
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button disabled={loading} className="w-full bg-blue-600 text-white rounded px-3 py-2">{loading? 'Signing in...' : 'Sign in'}</button>
      </form>
      <div className="my-4 text-center text-sm text-gray-500">or</div>
      <button onClick={handleGoogle} className="w-full bg-red-600 text-white rounded px-3 py-2">Continue with Google</button>
      <p className="mt-4 text-sm">No account? <Link className="text-blue-600" href="/sign-up">Sign up</Link></p>
    </main>
  );
}
