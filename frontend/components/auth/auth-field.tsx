export function AuthField({
  label,
  name,
  type = "text",
  placeholder,
  autoComplete,
  defaultValue,
  required = true
}: {
  label: string;
  name: string;
  type?: string;
  placeholder?: string;
  autoComplete?: string;
  defaultValue?: string;
  required?: boolean;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">{label}</span>
      <input
        name={name}
        type={type}
        placeholder={placeholder}
        autoComplete={autoComplete}
        defaultValue={defaultValue}
        required={required}
        className="form-input bg-white/90 dark:bg-slate-950/90"
      />
    </label>
  );
}
