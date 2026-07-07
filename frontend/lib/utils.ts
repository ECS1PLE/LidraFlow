export function field(formData: FormData, name: string): string {
  const value = formData.get(name);
  return typeof value === "string" ? value.trim() : "";
}

export function formatDate(value?: string) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

export function clip(value: string | undefined, length = 120) {
  if (!value) return "";
  return value.length > length ? `${value.slice(0, length - 1)}…` : value;
}

export function messagePath(path: string, message: string, level: "ok" | "warn" = "ok") {
  const url = new URL(path, "http://lidraflow.local");
  url.searchParams.set("msg", message);
  url.searchParams.set("level", level);
  return `${url.pathname}${url.search}`;
}
