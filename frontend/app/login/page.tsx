import Link from "next/link";
import { AuthField } from "@/components/auth/auth-field";
import { AuthShell } from "@/components/auth/auth-shell";
import { AuthSubmit } from "@/components/auth/auth-submit";
import { loginAction } from "@/lib/auth-actions";

export default function LoginPage({ searchParams }: { searchParams: { msg?: string; level?: string; next?: string } }) {
  return (
    <AuthShell
      eyebrow="LidraFlow Identity"
      title="Единый вход для AI-продаж"
      message={searchParams.msg}
      level={searchParams.level}
    >
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-600 dark:text-cyan-300">Welcome back</p>
        <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">Авторизация</h2>
        <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">Войди в рабочее пространство LidraFlow.</p>
      </div>

      <form action={loginAction} className="mt-7 space-y-4">
        <input type="hidden" name="next" value={searchParams.next ?? "/leads"} />
        <AuthField label="Email или логин" name="identifier" autoComplete="username" placeholder="admin или admin@lidraflow.local" />
        <div>
          <div className="mb-2 flex items-center justify-between gap-3">
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Пароль</span>
            <Link href="/restore" className="text-sm font-semibold text-cyan-600 transition hover:text-cyan-500 dark:text-cyan-300">
              Забыли пароль?
            </Link>
          </div>
          <input
            name="password"
            type="password"
            autoComplete="current-password"
            required
            className="form-input bg-white/90 dark:bg-slate-950/90"
            placeholder="••••••••"
          />
        </div>
        <AuthSubmit>Продолжить →</AuthSubmit>
      </form>

      <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
        Нет аккаунта? <Link href="/register" className="font-semibold text-slate-950 transition hover:text-cyan-600 dark:text-white dark:hover:text-cyan-300">Создать доступ</Link>
      </p>
    </AuthShell>
  );
}
