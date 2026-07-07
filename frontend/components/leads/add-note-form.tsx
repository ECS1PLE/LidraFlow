import { addNoteAction } from "@/lib/actions";

export function AddNoteForm({ leadId }: { leadId: number }) {
  const addNote = addNoteAction.bind(null, leadId);

  return (
    <form action={addNote} className="card space-y-4">
      <div>
        <h2 className="text-lg font-semibold">Внутренняя заметка</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Не отправляется клиенту, остаётся в истории CRM.</p>
      </div>
      <textarea name="body" rows={3} className="form-input" placeholder="Что важно помнить по этому лиду" />
      <button className="btn-secondary" type="submit">Добавить заметку</button>
    </form>
  );
}
