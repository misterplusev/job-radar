import { postedLabel, safeJobUrl } from './job-board-core.mjs'
export const STANDALONE_UI_VERSION = '2026-11-10.2'
export const escapeHTML = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))
export function jobCardMarkup(job, { logoUrl = '', applied = false } = {}) {
  const e = escapeHTML, name = job.company || job.team || 'Employer', url = safeJobUrl(job.url)
  const logo = safeJobUrl(logoUrl), initials = name.split(/\s+/).map(s=>s[0]).join('').slice(0,2).toUpperCase()
  return `<article class="job-card">
    <div class="job-card-heading"><span class="job-logo"><span>${e(initials)}</span>${logo ? `<img loading="lazy" src="${e(logo)}" alt="${e(name)} logo" onerror="this.hidden=true">` : ''}</span>
      <div class="job-identity"><span class="job-company">${e(name)}</span><h2 class="job-title">${url ? `<a href="${e(url)}" target="_blank" rel="noopener noreferrer">${e(job.title)}</a>` : e(job.title)}</h2></div>
      <div class="job-actions">${url ? `<a href="${e(url)}" target="_blank" rel="noopener noreferrer">Open listing ↗</a>` : ''}<button type="button" class="apply-btn" aria-pressed="${applied}" data-c="${e(job.company)}" data-u="${e(job.url)}" data-t="${e(job.title)}">${applied ? 'Applied ✓' : 'Mark applied'}</button></div>
    </div>
    <p class="job-location">${e(job.location || 'Location not listed')}</p>
    <div class="job-meta"><span>Posted: ${e(postedLabel(job.posted_at))}</span>${job.ats || job.platform ? `<span>${e(job.ats || job.platform)}</span>` : ''}${job.league ? `<span>${e(job.league)}</span>` : ''}<span class="job-badge${job.is_active ? '' : ' closed'}">${job.is_active ? 'Active' : 'Closed'}</span>${/remote/i.test(job.location || '') ? '<span class="job-badge">Remote</span>' : ''}${applied ? '<span class="job-badge applied">Applied</span>' : ''}</div>
    ${job.salary ? `<p class="job-salary">${e(job.salary)}</p>` : ''}
    <details class="job-details" data-id="${e(job.id)}"><summary>Job description</summary><div class="job-description">Open to load the description.</div></details>
  </article>`
}
export function wireJobDetails(container, { url, key, table }) {
  if (!['robotics_jobs','tech_jobs','team_jobs'].includes(table)) throw new Error('Unknown job source')
  const cache = new Map()
  container.addEventListener('toggle', async (event) => {
    const detail = event.target
    if (!detail.matches?.('.job-details') || !detail.open || detail.dataset.loaded) return
    const content = detail.querySelector('.job-description'), id = detail.dataset.id
    detail.dataset.loaded = 'true'
    if (cache.has(id)) { content.textContent = cache.get(id); return }
    content.textContent = 'Loading description…'
    try {
      const params = new URLSearchParams({ select:'description', id:`eq.${id}`, limit:'1' })
      const response = await fetch(`${url}/rest/v1/${table}?${params}`, { headers:{apikey:key,Authorization:`Bearer ${key}`},signal:AbortSignal.timeout(15000) })
      if (!response.ok) throw new Error('Description unavailable')
      const rows = await response.json()
      const text = String(rows[0]?.description || 'Description unavailable. Open the employer listing.').replace(/<[^>]*>/g,' ').replace(/&nbsp;/g,' ').replace(/&amp;/g,'&').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&lt;/g,'<').replace(/&gt;/g,'>')
      if (cache.size >= 300) cache.delete(cache.keys().next().value)
      cache.set(id,text);content.textContent=text
    } catch { content.textContent='Description unavailable. Open the employer listing.';delete detail.dataset.loaded }
  }, true)
}
export function wireCompanyScroll(scroller, left, right) {
  const scroll = (direction) => scroller.scrollBy({left:direction * Math.max(240,scroller.clientWidth * .7),behavior:globalThis.matchMedia?.('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'})
  left.addEventListener('click',()=>scroll(-1));right.addEventListener('click',()=>scroll(1))
}
