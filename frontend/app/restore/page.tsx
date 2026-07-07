import Link from "next/link";
import { AuthField } from "@/components/auth/auth-field";
import { AuthShell } from "@/components/auth/auth-shell";
import { AuthSubmit } from "@/components/auth/auth-submit";
import { forgotPasswordAction, resetPasswordAction } from "@/lib/auth-actions";

export default function RestorePage({
  searchParams
}: {
  searchParams: { identifier?: string; code?: string; msg?: string; level?: string };
}) {
  const hasCode = Boolean(searchParams.code);

  return (
    <AuthShell
      eyebrow="Account recovery"
      title="Верни доступ к LidraFlow"
      description="Сначала создай код восстановления, затем задай новый пароль. В MVP код показывается на экране, чтобы проект работал без SMTP-сервера."
      message={searchParams.msg}
      level={searchParams.level}
    >
      {!hasCode ? (
        <>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-600 dark:text-cyan-300">Recovery</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">Восстановить пароль</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">Укажи email или логин аккаунта, чтобы создать reset-код.</p>
          </div>
          <form action={forgotPasswordAction} className="mt-7 space-y-4">
            <AuthField label="Email или логин" name="identifier" autoComplete="username" defaultValue={searchParams.identifier ?? ""} placeholder="you@company.ru" />
            <AuthSubmit>Получить код →</AuthSubmit>
          </form>
        </>
      ) : (
        <>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-600 dark:text-cyan-300">Reset password</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">Новый пароль</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">Код уже подставлен. Задай новый пароль для аккаунта.</p>
          </div>
          <div className="mt-6 rounded-2xl border border-cyan-200 bg-cyan-50 p-4 text-xs leading-5 text-cyan-950 dark:border-cyan-900/60 dark:bg-cyan-950/35 dark:text-cyan-100">
            Reset-код MVP: <code className="break-all font-semibold">{searchParams.code}</code>
          </div>
          <form action={resetPasswordAction} className="mt-7 space-y-4">
            <input type="hidden" name="identifier" value={searchParams.identifier ?? ""} />
            <input type="hidden" name="code" value={searchParams.code ?? ""} />
            <AuthField label="Email или логин" name="identifier_readonly" defaultValue={searchParams.identifier ?? ""} required={false} />
            <div className="grid gap-4 sm:grid-cols-2">
              <AuthField label="Новый пароль" name="password" type="password" autoComplete="new-password" placeholder="Минимум 8" />
              <AuthField label="Повторите пароль" name="password_repeat" type="password" autoComplete="new-password" placeholder="Ещё раз" />
            </div>
            <AuthSubmit>Сменить пароль →</AuthSubmit>
          </form>
        </>
      )}

      <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
        Вспомнили пароль? <Link href="/login" className="font-semibold text-slate-950 transition hover:text-cyan-600 dark:text-white dark:hover:text-cyan-300">Вернуться ко входу</Link>
      </p>
    </AuthShell>
  );
}
