export function AuthSubmit({ children }: { children: React.ReactNode }) {
  return (
    <button type="submit" className="btn-primary w-full !rounded-2xl !py-3.5 text-base">
      {children}
    </button>
  );
}
