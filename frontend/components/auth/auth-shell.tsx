import Link from "next/link";
import { ThemeToggle } from "@/components/theme-toggle";
import { Toast } from "@/components/toast";

export function AuthShell({
  eyebrow,
  title,
  description,
  children,
  message,
  level
}: {
  eyebrow: string;
  title: string;
  description?: string;
  children: React.ReactNode;
  message?: string;
  level?: string;
}) {
  return (
    <main className="relative min-h-screen overflow-hidden px-5 py-6 sm:px-8">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -left-28 top-16 h-72 w-72 rounded-full bg-indigo-400/20 blur-3xl dark:bg-indigo-500/20" />
        <div className="absolute -right-24 bottom-16 h-80 w-80 rounded-full bg-cyan-300/20 blur-3xl dark:bg-cyan-400/10" />
        <div className="absolute left-1/2 top-1/2 h-[34rem] w-[34rem] -translate-x-1/2 -translate-y-1/2 rounded-full border border-white/50 bg-white/20 shadow-[0_0_120px_rgba(15,23,42,0.08)] backdrop-blur-3xl dark:border-white/10 dark:bg-white/5" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(148,163,184,0.16)_1px,transparent_1px),linear-gradient(to_bottom,rgba(148,163,184,0.16)_1px,transparent_1px)] bg-[size:72px_72px] [mask-image:radial-gradient(circle_at_center,black,transparent_72%)]" />
      </div>

      <div className="relative mx-auto flex min-h-[calc(100vh-3rem)] w-full max-w-6xl flex-col">
        <header className="flex items-center justify-between">
          <Link href="/login" className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-[1.25rem] bg-slate-950 text-xl font-black text-white shadow-lg shadow-slate-950/10 dark:bg-white dark:text-slate-950">L</div>
            <div>
              <p className="text-lg font-semibold tracking-tight text-slate-950 dark:text-white">LidraFlow SSO</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">Единый вход в омниканальный AI SDR</p>
            </div>
          </Link>
          <ThemeToggle />
        </header>

        <section className="grid flex-1 items-center gap-10 py-12 lg:grid-cols-[1fr_30rem]">
          <div className="max-w-2xl">
            <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white/70 px-4 py-2 text-xs font-semibold uppercase tracking-[0.22em] text-slate-500 shadow-sm backdrop-blur dark:border-slate-800 dark:bg-slate-950/60 dark:text-slate-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_0_4px_rgba(52,211,153,0.14)]" />
              {eyebrow}
            </div>
            <h1 className="text-4xl font-semibold tracking-[-0.04em] text-slate-950 dark:text-white sm:text-6xl">
              {title}
            </h1>
            <p className="mt-5 max-w-xl text-base leading-8 text-slate-600 dark:text-slate-300">
              {description}
            </p>
          </div>

          <div className="relative">
            <div className="absolute -inset-4 rounded-[2rem] bg-gradient-to-br from-slate-900/10 to-indigo-500/10 blur-2xl dark:from-white/10 dark:to-indigo-500/20" />
            <div className="relative rounded-[2rem] border border-white/80 bg-white/90 p-6 shadow-2xl shadow-slate-950/10 backdrop-blur-xl dark:border-slate-800 dark:bg-slate-950/85 dark:shadow-black/30 sm:p-8">
              <Toast message={message} level={level} />
              {children}
            </div>
          </div>
        </section>

        <footer className="pb-4 text-center text-xs text-slate-400">
          © LidraFlow
        </footer>
      </div>
    </main>
  );
}
