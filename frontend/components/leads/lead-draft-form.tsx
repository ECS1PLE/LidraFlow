import { makeDraftAction } from "@/lib/actions";

export function LeadDraftForm({ leadId }: { leadId: number }) {
  const makeDraft = makeDraftAction.bind(null, leadId);

  return (
    <form action={makeDraft} className="card space-y-4">
      <div>
        <h2 className="text-lg font-semibold">AI-черновик</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Сгенерирует короткое первое касание по шаблону и настройкам компании.</p>
      </div>
      <textarea name="extra_context" rows={3} className="form-input" placeholder="Дополнительный контекст: акция, ниша, повод, ограничение по тону" />
      <button className="btn-primary" type="submit">Создать черновик</button>
    </form>
  );
}
