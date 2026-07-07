import Link from "next/link";
import { ThemeToggle } from "@/components/theme-toggle";
import { logoutAction } from "@/lib/auth-actions";
import { getCurrentSession } from "@/lib/auth";

export async function AppShell({ children }: { children: React.ReactNode }) {
  const session = await getCurrentSession();
  const displayName = session?.name || session?.email || "Аккаунт";

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-5 py-6 sm:px-8">
      <header className="mb-8 flex flex-col gap-4 rounded-[2rem] border border-white/70 bg-white/80 p-4 shadow-sm backdrop-blur dark:border-slate-800 dark:bg-slate-950/70 md:flex-row md:items-center md:justify-between">
        <Link href="/leads" className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-950 text-lg font-black text-white dark:bg-white dark:text-slate-950">L</div>
          <div>
            <p className="text-lg font-semibold tracking-tight">LidraFlow</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">AI SDR для локального B2B</p>
          </div>
        </Link>
        <nav className="flex flex-wrap items-center gap-2">
          <Link href="/leads" className="rounded-full px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900">Лиды</Link>
          <Link href="/leads/new" className="rounded-full px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900">Новый лид</Link>
          <Link href="/discover" className="rounded-full px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900">Поиск</Link>
          <Link href="/broadcast" className="rounded-full px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900">Рассылка</Link>
          <Link href="/settings" className="rounded-full px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900">Настройки</Link>
          <div className="ml-0 flex items-center gap-2 rounded-full border border-slate-200 bg-white px-2 py-1 dark:border-slate-800 dark:bg-slate-900 md:ml-2">
            <span className="hidden max-w-[130px] truncate pl-2 text-xs font-medium text-slate-500 dark:text-slate-400 sm:inline">{displayName}</span>
            <form action={logoutAction}>
              <button type="submit" className="rounded-full px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800">Выйти</button>
            </form>
          </div>
          <ThemeToggle />
        </nav>
      </header>
      <main className="flex-1">{children}</main>
    </div>
  );
}
