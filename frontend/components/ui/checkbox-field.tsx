type CheckboxFieldProps = {
  name: string;
  defaultChecked?: boolean;
  title: string;
  description: string;
};

export function CheckboxField({ name, defaultChecked, title, description }: CheckboxFieldProps) {
  return (
    <label className="flex items-start gap-3 text-sm text-slate-700 dark:text-slate-300">
      <input name={name} type="checkbox" defaultChecked={defaultChecked} className="mt-1" />
      <span>
        <b>{title}</b> {description}
      </span>
    </label>
  );
}
