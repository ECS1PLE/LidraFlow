import type { ConsentStatus, LeadStatus, MessageDirection } from "./types";

export const fallbackStatusLabels: Record<LeadStatus, string> = {
  new: "Новый",
  drafted: "Есть черновик",
  contacted: "Написали",
  replied: "Ответил",
  qualified: "Квалифицирован",
  closed: "Закрыт"
};

export const fallbackConsentLabels: Record<ConsentStatus, string> = {
  pending: "Нет согласия / только черновик",
  opted_in: "Можно отвечать",
  opted_out: "Не писать"
};

export const directionLabels: Record<MessageDirection, string> = {
  in: "Входящее",
  out: "Отправлено",
  draft: "Черновик AI",
  system: "Заметка"
};

export function statusTone(status: string) {
  if (status === "qualified") return "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300";
  if (status === "replied") return "bg-sky-100 text-sky-700 dark:bg-sky-900/40 dark:text-sky-300";
  if (status === "closed") return "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300";
  if (status === "contacted") return "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300";
  if (status === "drafted") return "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300";
  return "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300";
}

export function consentTone(status: string) {
  if (status === "opted_in") return "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300";
  if (status === "opted_out") return "bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300";
  return "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300";
}
