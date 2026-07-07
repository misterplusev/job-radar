export const dynamic = "force-dynamic";

import RadarBoard from "./RadarBoard";

async function sb(path: string) {
  const base = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!base || !anon) return null;
  const res = await fetch(`${base.replace(/\/+$/, "")}/rest/v1/${path}`, {
    headers: { apikey: anon, Authorization: `Bearer ${anon}` },
    cache: "no-store",
  });
  if (!res.ok) return [];
  return res.json();
}

export default async function Page() {
  const rows = await sb("radar?select=*&order=fit_score.desc&limit=1500");
  const sources = await sb("source_health?select=*");

  if (rows === null) {
    return (
      <main style={{ padding: 40, fontFamily: "system-ui", color: "#e8e8e8" }}>
        <h1>Job Radar</h1>
        <p style={{ color: "#fca5a5" }}>Not configured. Set <code>NEXT_PUBLIC_SUPABASE_URL</code> and
          <code> NEXT_PUBLIC_SUPABASE_ANON_KEY</code> in the Vercel project env.</p>
      </main>
    );
  }
  return <RadarBoard rows={rows} sources={sources || []} />;
}
