import { NextResponse } from "next/server";

// Server-side application logging (uses the service-role key; never exposed to the browser).
export async function POST(req: Request) {
  const body = await req.json().catch(() => ({}));
  const { company, job_url, job_title, status = "applied", fit_score } = body || {};
  if (!company || !job_url) {
    return NextResponse.json({ error: "company and job_url required" }, { status: 400 });
  }
  const base = process.env.NEXT_PUBLIC_SUPABASE_URL?.replace(/\/+$/, "");
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!base || !key) return NextResponse.json({ error: "server not configured" }, { status: 500 });

  const res = await fetch(`${base}/rest/v1/applications?on_conflict=company,job_url`, {
    method: "POST",
    headers: { apikey: key, Authorization: `Bearer ${key}`, "Content-Type": "application/json",
               Prefer: "resolution=merge-duplicates" },
    body: JSON.stringify([{ company, job_url, job_title, status, fit_score,
                            applied_at: status === "applied" ? new Date().toISOString() : null }]),
  });
  if (!res.ok) return NextResponse.json({ error: await res.text() }, { status: 500 });
  return NextResponse.json({ ok: true, status });
}
