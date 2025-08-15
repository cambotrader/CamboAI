import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";

export default async function ProfilePage() {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/sign-in');

  async function signOut() {
    "use server";
    const supabase = createClient();
    await supabase.auth.signOut();
    return redirect('/');
  }

  return (
    <main className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold mb-2">Profile</h1>
      <p className="mb-6">{user.email}</p>
      <form action={signOut}>
        <button className="px-3 py-2 rounded bg-gray-200 dark:bg-gray-800" type="submit">Sign out</button>
      </form>
    </main>
  );
}
