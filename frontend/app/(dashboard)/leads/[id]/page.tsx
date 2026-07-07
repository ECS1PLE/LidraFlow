export const dynamic = "force-dynamic";

import { BackendError } from "@/components/backend-error";
import { AddNoteForm } from "@/components/leads/add-note-form";
import { LeadCardForm } from "@/components/leads/lead-card-form";
import { LeadDraftForm } from "@/components/leads/lead-draft-form";
import { LeadHeader } from "@/components/leads/lead-header";
import { LeadStatusForm } from "@/components/leads/lead-status-form";
import { MessageThread } from "@/components/leads/message-thread";
import { SendMessageForm } from "@/components/leads/send-message-form";
import { Toast } from "@/components/toast";
import { getLead } from "@/lib/api";

export default async function LeadDetailPage({ params, searchParams }: { params: { id: string }; searchParams: { msg?: string; level?: string } }) {
  try {
    const leadId = Number(params.id);
    const data = await getLead(leadId);
    const { lead, messages } = data;
    const lastDraft = [...messages].reverse().find((message) => message.direction === "draft")?.body ?? "";

    return (
      <div>
        <Toast message={searchParams.msg} level={searchParams.level} />
        <LeadHeader
          lead={lead}
          statusLabels={data.status_labels}
          consentLabels={data.consent_labels}
          channelLabels={data.channel_labels}
        />

        <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
          <div className="space-y-6">
            <LeadCardForm lead={lead} />
            <LeadStatusForm lead={lead} statusLabels={data.status_labels} consentLabels={data.consent_labels} />
            <LeadDraftForm leadId={lead.id} />
          </div>

          <div className="space-y-6">
            <MessageThread messages={messages} channelLabels={data.channel_labels} />
            <SendMessageForm lead={lead} lastDraft={lastDraft} />
            <AddNoteForm leadId={lead.id} />
          </div>
        </div>
      </div>
    );
  } catch (error) {
    return <BackendError error={error} />;
  }
}
