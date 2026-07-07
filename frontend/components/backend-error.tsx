export function BackendError({ error }: { error: unknown }) {
  const message = error instanceof Error ? error.message : "Неизвестная ошибка";
  return (
    <div className="rounded-3xl border border-rose-200 bg-rose-50 p-8 text-rose-900 shadow-soft dark:border-rose-900/60 dark:bg-rose-950/30 dark:text-rose-100">
      <p className="text-sm font-semibold uppercase tracking-[0.2em] text-rose-500 dark:text-rose-300">API недоступен</p>
      <h1 className="mt-3 text-2xl font-semibold">Не удалось подключиться к backend</h1>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-rose-800 dark:text-rose-100/80">
        Проверь, что FastAPI запущен на <code>http://127.0.0.1:8000</code>, а в <code>frontend/.env.local</code> указан тот же <code>LIDRAFLOW_API_KEY</code>, что и <code>FRONTEND_API_KEY</code> в <code>config/secrets.env</code>.
      </p>
      <pre className="mt-5 overflow-auto rounded-2xl bg-white/70 p-4 text-xs dark:bg-slate-950/60">{message}</pre>
    </div>
  );
}
