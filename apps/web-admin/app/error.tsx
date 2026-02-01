"use client";

import { useEffect } from "react";

export default function GlobalError({ error }: { error: Error }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main className="main">
      <section className="panel">
        <h2>Something went wrong</h2>
        <p className="status">Try refreshing the page or contact support.</p>
      </section>
    </main>
  );
}
