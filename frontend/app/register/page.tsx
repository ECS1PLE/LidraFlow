import Link from "next/link";
import { AuthField } from "@/components/auth/auth-field";
import { AuthShell } from "@/components/auth/auth-shell";
import { AuthSubmit } from "@/components/auth/auth-submit";
import { registerAction } from "@/lib/auth-actions";

export default function RegisterPage({ searchParams }: { searchParams: { msg?: string; level?: string } }) {
  return (
    <AuthShell
      eyebrow="LidraFlow Workspace"
      title="Создай доступ для команды"
      description="Регистрация добавляет пользователя в локальный SSO-слой проекта. После входа можно подключать Telegram, WhatsApp, MAX, VK и запускать кампании по географии."
      message={searchParams.msg}
      level={searchParams.level}
    >
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-600 dark:text-cyan-300">New workspace user</p>
        <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">Регистрация</h2>
        <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">Добавь владельца или менеджера рабочего пространства.</p>
      </div>

      <form action={registerAction} className="mt-7 space-y-4">
        <AuthField label="Имя" name="full_name" autoComplete="name" placeholder="Алексей" />
        <AuthField label="Компания" name="company_name" autoComplete="organization" placeholder="Aeterna / LidraFlow" required={false} />
        <div className="grid gap-4 sm:grid-cols-2">
          <AuthField label="Логин" name="username" autoComplete="username" placeholder="alex" required={false} />
          <AuthField label="Почта" name="email" type="email" autoComplete="email" placeholder="you@company.ru" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <AuthField label="Пароль" name="password" type="password" autoComplete="new-password" placeholder="Минимум 8 символов" />
          <AuthField label="Повторите пароль" name="password_repeat" type="password" autoComplete="new-password" placeholder="Ещё раз" />
        </div>
        <AuthSubmit>Создать аккаунт →</AuthSubmit>
      </form>

      <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
        Уже есть доступ? <Link href="/login" className="font-semibold text-slate-950 transition hover:text-cyan-600 dark:text-white dark:hover:text-cyan-300">Войти</Link>
      </p>
    </AuthShell>
  );
}
