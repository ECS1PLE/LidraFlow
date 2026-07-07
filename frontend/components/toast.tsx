type ToastProps = {
  message?: string;
  level?: string;
};

export function Toast({ message, level = "ok" }: ToastProps) {
  if (!message) return null;
  const tone =
    level === "warn"
      ? "border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-900/60 dark:bg-amber-950/40 dark:text-amber-200"
      : "border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-900/60 dark:bg-emerald-950/40 dark:text-emerald-200";

  return <div className={`mb-6 rounded-2xl border px-4 py-3 text-sm ${tone}`}>{message}</div>;
}
