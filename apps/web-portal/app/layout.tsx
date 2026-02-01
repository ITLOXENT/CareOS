import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header style={{ padding: "16px 0" }}>
          <nav style={{ display: "flex", gap: "12px" }}>
            <a href="/">Home</a>
            <a href="/profile">Profile</a>
            <a href="/patients">Patients</a>
            <a href="/episodes">Episodes</a>
            <a href="/notifications">Notifications</a>
          </nav>
        </header>
        {children}
      </body>
    </html>
  );
}
