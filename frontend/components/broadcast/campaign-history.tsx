import type { Campaign, LabelMap } from "@/lib/types";
import { formatDate } from "@/lib/utils";

type CampaignHistoryProps = {
  campaigns: Campaign[];
  channelLabels: LabelMap;
};

export function CampaignHistory({ campaigns, channelLabels }: CampaignHistoryProps) {
  return (
    <div className="card space-y-4">
      <h2 className="text-lg font-semibold">Последние кампании</h2>
      {campaigns.length === 0 ? (
        <p className="text-sm text-slate-500 dark:text-slate-400">Запусков пока нет.</p>
      ) : (
        <div className="space-y-3">
          {campaigns.slice(0, 8).map((campaign) => (
            <article key={campaign.id} className="rounded-3xl border border-slate-200 p-4 text-sm dark:border-slate-800">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-semibold text-slate-900 dark:text-white">{campaign.name || "Без названия"}</p>
                  <p className="mt-1 text-xs text-slate-400">{formatDate(campaign.created_at)} · {channelLabels[campaign.channel] ?? campaign.channel}</p>
                </div>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                  {campaign.dry_run ? "dry-run" : "send"}
                </span>
              </div>
              <p className="mt-3 text-slate-500 dark:text-slate-400">Подходящих: {campaign.eligible}; отправлено: {campaign.sent}; ошибок: {campaign.failed}; пропущено: {campaign.skipped}</p>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
