import Sidebar from "@/components/sidebar"
import "../globals.css"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-950 text-gray-100">
      <div className="flex">
        <Sidebar />
        <main className="flex-1 min-h-screen">
          <div className="p-4 md:p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}