"use client";

import { useMemo, useState } from "react";

type Row = {
  id: number; company: string; title: string; url: string; location: string | null;
  source: string | null; remote: boolean | null; is_active: boolean; is_new: boolean;
  fit_score: number; archetype: string | null; rationale: string | null;
  applied: boolean; applied_status: string | null;
};
type Source = { source: string; last_run: string | null; ok_runs: number; err_runs: number; total_jobs_seen: number };

const S = {
  input: { background: "#0c0c0e", color: "#eee", border: "1px solid #2a2a2a", borderRadius: 8, padding: 8 } as const,
  pill: { fontSize: 11, padding: "2px 7px", border: "1px solid #2a2a2a", borderRadius: 999, color: "#bcbcbc" } as const,
};

function color(s: number) { return s >= 85 ? "#6ee7b7" : s >= 70 ? "#fcd34d" : "#9aa0a6"; }

export default function RadarBoard({ rows, sources }: { rows: Row[]; sources: Source[] }) {
  const [q, setQ] = useState("");
  const [minScore, setMinScore] = useState(70);
  const [source, setSource] = useState("");
  const [archetype, setArchetype] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [hideApplied, setHideApplied] = useState(true);
  const [activeOnly, setActiveOnly] = useState(true);

  const sourceOpts = useMemo(() => [...new Set(rows.map(r => r.source).filter(Boolean))].sort() as string[], [rows]);
  const archetypeOpts = useMemo(() => [...new Set(rows.map(r => r.archetype).filter(Boolean))].sort() as string[], [rows]);

  const filtered = useMemo(() => rows.filter(r => {
    if (r.fit_score < minScore) return false;
    if (source && r.source !== source) return false;
    if (archetype && r.archetype !== archetype) return false;
    if (remoteOnly && !r.remote && !/remote/i.test(r.location || "")) return false;
    if (hideApplied && r.applied) return false;
    if (activeOnly && r.is_active === false) return false;
    const t = q.trim().toLowerCase();
    return !t || `${r.title} ${r.company} ${r.location}`.toLowerCase().includes(t);
  }), [rows, q, minScore, source, archetype, remoteOnly, hideApplied, activeOnly]);

  async function markApplied(r: Row) {
    const res = await fetch("/api/apply", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ company: r.company, job_url: r.url, job_title: r.title,
                             status: r.applied ? "archived" : "applied", fit_score: r.fit_score }),
    });
    if (res.ok) location.reload(); else alert("apply toggle failed: " + (await res.text()));
  }

  return (
    <main style={{ fontFamily: "system-ui", color: "#e8e8e8" }}>
      <header style={{ padding: "16px 20px", borderBottom: "1px solid #222" }}>
        <h1 style={{ margin: 0, fontSize: 20 }}>Job Radar</h1>
        <div style={{ color: "#8a8a8a", fontSize: 12, marginTop: 4 }}>{filtered.length} of {rows.length} matches</div>
      </header>

      {/* sources health strip */}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", padding: "10px 20px", borderBottom: "1px solid #161616" }}>
        {sources.map(s => (
          <span key={s.source} title={`last run ${s.last_run || "?"} · ${s.total_jobs_seen} jobs seen`} style={S.pill}>
            {s.source}: <b style={{ color: s.err_runs ? "#fca5a5" : "#6ee7b7" }}>{s.ok_runs}✓</b>
            {s.err_runs ? <span style={{ color: "#fca5a5" }}> {s.err_runs}✗</span> : null}
          </span>
        ))}
      </div>

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", padding: "12px 20px", position: "sticky", top: 0, background: "#050506", borderBottom: "1px solid #1a1a1a" }}>
        <input style={{ ...S.input, minWidth: 260 }} placeholder="search title / company / location" value={q} onChange={e => setQ(e.target.value)} />
        <label style={{ color: "#cfcfcf" }}>min <input type="number" value={minScore} min={0} max={100} onChange={e => setMinScore(+e.target.value)} style={{ ...S.input, width: 64 }} /></label>
        <select style={S.input} value={source} onChange={e => setSource(e.target.value)}><option value="">all sources</option>{sourceOpts.map(s => <option key={s}>{s}</option>)}</select>
        <select style={S.input} value={archetype} onChange={e => setArchetype(e.target.value)}><option value="">all types</option>{archetypeOpts.map(a => <option key={a}>{a}</option>)}</select>
        <label style={{ color: "#cfcfcf" }}><input type="checkbox" checked={remoteOnly} onChange={e => setRemoteOnly(e.target.checked)} /> remote</label>
        <label style={{ color: "#cfcfcf" }}><input type="checkbox" checked={hideApplied} onChange={e => setHideApplied(e.target.checked)} /> hide applied</label>
        <label style={{ color: "#cfcfcf" }}><input type="checkbox" checked={activeOnly} onChange={e => setActiveOnly(e.target.checked)} /> active only</label>
      </div>

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead><tr>{["Fit", "Title", "Company", "Type", "Location", "Source", ""].map(h =>
          <th key={h} style={{ textAlign: "left", padding: "8px 12px", borderBottom: "1px solid #222", position: "sticky", top: 108, background: "#0a0a0b", fontSize: 12 }}>{h}</th>)}</tr></thead>
        <tbody>
          {filtered.map(r => (
            <tr key={r.id} style={{ opacity: r.applied ? 0.5 : 1 }}>
              <td style={{ padding: "8px 12px", fontWeight: 800, color: color(r.fit_score), borderBottom: "1px solid #141414" }}>{r.fit_score}</td>
              <td style={{ padding: "8px 12px", borderBottom: "1px solid #141414" }}>
                <a href={r.url} target="_blank" rel="noreferrer" style={{ color: "#7aa2ff" }}>{r.title}</a>
                {r.is_new ? <span style={{ ...S.pill, marginLeft: 6, color: "#6ee7b7", borderColor: "#215" }}>NEW</span> : null}
                <div style={{ color: "#8a8a8a", fontSize: 12 }}>{(r.rationale || "").slice(0, 160)}</div>
              </td>
              <td style={{ padding: "8px 12px", borderBottom: "1px solid #141414" }}>{r.company}</td>
              <td style={{ padding: "8px 12px", borderBottom: "1px solid #141414" }}><span style={S.pill}>{r.archetype}</span></td>
              <td style={{ padding: "8px 12px", borderBottom: "1px solid #141414", fontSize: 13 }}>{r.location}</td>
              <td style={{ padding: "8px 12px", borderBottom: "1px solid #141414" }}><span style={S.pill}>{r.source}</span></td>
              <td style={{ padding: "8px 12px", borderBottom: "1px solid #141414" }}>
                <button onClick={() => markApplied(r)} style={{ ...S.input, cursor: "pointer" }}>{r.applied ? "applied ✓" : "mark applied"}</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
