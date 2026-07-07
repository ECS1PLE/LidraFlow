import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LidraFlow",
  description: "AI SDR для локального B2B"
};

function ThemeInitScript() {
  const script = `
    try {
      var saved = localStorage.getItem('lidraflow-theme');
      var systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      var theme = saved || (systemDark ? 'dark' : 'light');
      document.documentElement.classList.toggle('dark', theme === 'dark');
    } catch (_) {}
  `;
  return <script dangerouslySetInnerHTML={{ __html: script }} />;
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <head>
        <ThemeInitScript />
      </head>
      <body className="text-slate-900 antialiased dark:text-slate-100">{children}</body>
    </html>
  );
}
