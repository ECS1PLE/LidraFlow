"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { apiFetch } from "../api";
import { field, messagePath } from "../utils";
import { leadPayload } from "./helpers";

export async function createLeadAction(formData: FormData) {
  const data = await apiFetch<{ lead: { id: number } }>("/api/leads", {
    method: "POST",
    body: JSON.stringify(leadPayload(formData))
  });
  revalidatePath("/leads");
  redirect(messagePath(`/leads/${data.lead.id}`, "Лид создан"));
}

export async function updateLeadAction(leadId: number, formData: FormData) {
  await apiFetch(`/api/leads/${leadId}`, {
    method: "PATCH",
    body: JSON.stringify(leadPayload(formData))
  });
  revalidatePath(`/leads/${leadId}`);
  redirect(messagePath(`/leads/${leadId}`, "Карточка обновлена"));
}

export async function updateStatusAction(leadId: number, formData: FormData) {
  await apiFetch(`/api/leads/${leadId}/status`, {
    method: "PATCH",
    body: JSON.stringify({
      status: field(formData, "status"),
      consent_status: field(formData, "consent_status")
    })
  });
  revalidatePath(`/leads/${leadId}`);
  redirect(messagePath(`/leads/${leadId}`, "Статусы обновлены"));
}

export async function importLeadsAction(formData: FormData) {
  const apiForm = new FormData();
  const file = formData.get("file");
  if (file instanceof File) {
    apiForm.set("file", file);
  }
  const data = await apiFetch<{ imported: number; warnings: string[] }>("/api/leads/import", {
    method: "POST",
    body: apiForm
  });
  revalidatePath("/leads");
  const level = data.imported > 0 ? "ok" : "warn";
  const warningText = data.warnings.length ? `; предупреждений: ${data.warnings.length}` : "";
  redirect(messagePath("/leads", `Импортировано лидов: ${data.imported}${warningText}`, level));
}

export async function makeDraftAction(leadId: number, formData: FormData) {
  await apiFetch(`/api/leads/${leadId}/draft`, {
    method: "POST",
    body: JSON.stringify({ extra_context: field(formData, "extra_context") })
  });
  revalidatePath(`/leads/${leadId}`);
  redirect(messagePath(`/leads/${leadId}`, "Черновик создан"));
}

export async function sendMessageAction(leadId: number, formData: FormData) {
  let message = "Сообщение отправлено";
  let level: "ok" | "warn" = "ok";
  try {
    await apiFetch(`/api/leads/${leadId}/send`, {
      method: "POST",
      body: JSON.stringify({
        body: field(formData, "body"),
        channel: field(formData, "channel") || "auto",
        whatsapp_template_name: field(formData, "whatsapp_template_name"),
        whatsapp_language: field(formData, "whatsapp_language")
      })
    });
    revalidatePath(`/leads/${leadId}`);
  } catch (error) {
    message = error instanceof Error ? error.message : "Не удалось отправить сообщение";
    level = "warn";
  }
  redirect(messagePath(`/leads/${leadId}`, message, level));
}

export async function addNoteAction(leadId: number, formData: FormData) {
  await apiFetch(`/api/leads/${leadId}/note`, {
    method: "POST",
    body: JSON.stringify({ body: field(formData, "body") })
  });
  revalidatePath(`/leads/${leadId}`);
  redirect(messagePath(`/leads/${leadId}`, "Заметка добавлена"));
}

export async function deleteLeadAction(leadId: number) {
  await apiFetch(`/api/leads/${leadId}`, { method: "DELETE" });
  revalidatePath("/leads");
  redirect(messagePath("/leads", "Лид удалён"));
}
