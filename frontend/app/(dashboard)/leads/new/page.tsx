import Link from "next/link";
import { LeadFormFields } from "@/components/leads/lead-form-fields";
import { createLeadAction } from "@/lib/actions";

export default function NewLeadPage() {
  return (
    <div className="mx-auto max-w-5xl">
      <div className="mb-6">
        <Link href="/leads" className="text-sm font-medium text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">← К лидам</Link>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950 dark:text-white">Новый лид</h1>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Добавь организацию вручную. Поля каналов можно заполнить сразу или позже после входящего сообщения/webhook.</p>
      </div>

      <form action={createLeadAction} className="card grid gap-5 md:grid-cols-2">
        <LeadFormFields mode="create" />
        <div className="md:col-span-2 flex flex-wrap gap-3">
          <button className="btn-primary" type="submit">Создать лид</button>
          <Link href="/leads" className="btn-secondary">Отмена</Link>
        </div>
      </form>
    </div>
  );
}
