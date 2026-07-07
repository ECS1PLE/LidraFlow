export function IntegrationStatus({ ok }: { ok: boolean }) {
  return (
    <span className={ok ? "text-emerald-600 dark:text-emerald-300" : "text-slate-400"}>
      {ok ? "подключено" : "не настроено"}
    </span>
  );
}
