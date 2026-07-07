import { updateLeadAction } from "@/lib/actions";
import type { Lead } from "@/lib/types";
import { LeadFormFields } from "./lead-form-fields";

export function LeadCardForm({ lead }: { lead: Lead }) {
  const updateLead = updateLeadAction.bind(null, lead.id);

  return (
    <form action={updateLead} className="card grid gap-4 md:grid-cols-2">
      <div className="md:col-span-2 flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">Карточка организации</h2>
        <button className="btn-secondary !py-2" type="submit">Сохранить</button>
      </div>
      <LeadFormFields lead={lead} mode="edit" />
    </form>
  );
}
