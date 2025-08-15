import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";

export default async function ProjectsPage() {
  const supabase = createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/sign-in');

  async function addProject(formData: FormData) {
    "use server";
    const supabase = createClient();
    const name = String(formData.get('name') || '').trim();
    if (!name) return;
    await supabase.from('projects').insert({ name });
  }

  const { data: projects } = await supabase
    .from('projects')
    .select('*')
    .order('created_at', { ascending: false });

  return (
    <main className="p-6 max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-semibold">Projects</h1>
      <form action={addProject} className="flex gap-2">
        <input name="name" placeholder="New project name" className="flex-1 border rounded px-3 py-2" />
        <button className="px-3 py-2 rounded bg-blue-600 text-white" type="submit">Add</button>
      </form>
      <ul className="space-y-2">
        {(projects ?? []).map((p: any) => (
          <li key={p.id} className="border rounded px-3 py-2">
            <div className="font-medium">{p.name}</div>
            <div className="text-xs text-gray-500">{new Date(p.created_at).toLocaleString()}</div>
          </li>
        ))}
      </ul>
    </main>
  );
}
