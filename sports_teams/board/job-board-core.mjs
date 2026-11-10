// Shared behavior for all four standalone boards and ABET jobs modules.
// Country classification uses stated location evidence, never company headquarters.
export const JOB_BOARD_VERSION = '2026-11-10.1'
export const RESULT_COUNTS = Object.freeze([100, 200, 500, 'all'])
export const DEFAULT_JOB_FILTERS = Object.freeze({ status: 'active', sort: 'newest', includeInternational: false, limit: 100 })

export function postedTime(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}(?:$|T|\s)/.test(value.trim())) return null
  const stamp = Date.parse(value)
  return Number.isFinite(stamp) ? stamp : null
}

export function postedLabel(value) {
  const stamp = postedTime(value)
  return stamp === null ? 'Date not provided' : new Date(stamp).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' })
}

export function compareJobs(a, b, sort = 'newest') {
  if (sort === 'newest' || sort === 'oldest') {
    const av = postedTime(a.posted_at), bv = postedTime(b.posted_at)
    // Unknown dates are LAST in either direction. Discovery/refresh dates never
    // substitute for the employer posting date.
    if (av === null && bv !== null) return 1
    if (bv === null && av !== null) return -1
    if (av !== null && bv !== null && av !== bv) return sort === 'oldest' ? av - bv : bv - av
  } else {
    const key = ['company', 'title', 'location'].includes(sort) ? sort : 'title'
    const cmp = String(a[key] || '').localeCompare(String(b[key] || ''), undefined, { sensitivity: 'base', numeric: true })
    if (cmp) return cmp
  }
  return String(a.company || a.team || '').localeCompare(String(b.company || b.team || '')) || String(a.title || '').localeCompare(String(b.title || '')) || String(a.id ?? a.url ?? '').localeCompare(String(b.id ?? b.url ?? ''), undefined, { numeric: true })
}

const US_EXPLICIT = /\b(?:united states(?: of america)?|u\.?s\.?a\.?|u\.s\.|us)\b/i
const US_EXCLUDED = /\b(?:outside|excluding|except|not in)\s+(?:the\s+)?(?:united states|usa|us)\b/i
const US_STATES = /\b(?:alabama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|florida|hawaii|idaho|illinois|indiana|iowa|kansas|kentucky|louisiana|maine|maryland|massachusetts|michigan|minnesota|mississippi|missouri|montana|nebraska|nevada|new hampshire|new jersey|new mexico|new york|north carolina|north dakota|ohio|oklahoma|oregon|pennsylvania|rhode island|south carolina|south dakota|tennessee|texas|utah|vermont|virginia|washington|west virginia|wisconsin|wyoming|district of columbia|puerto rico|guam|american samoa|u\.s\. virgin islands)\b/i
const US_STATE_CODE = /(?:,\s*|\s+-\s+)(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY|DC|PR)(?=\s*(?:\d{5}|$|[,;·•(/-]))/
const US_CITIES = /\b(?:san francisco|south san francisco|san diego|san jose|los angeles|seattle|redmond|bellevue|chandler|tempe|phoenix|scottsdale|tucson|denver|boulder|broomfield|boston|new york city|nyc|brooklyn|queens|manhattan|chicago|austin|dallas|houston|san antonio|fort worth|atlanta|miami|orlando|tampa|las vegas|reno|pittsburgh|philadelphia|detroit|minneapolis|milwaukee|nashville|memphis|charlotte|raleigh|durham|baltimore|columbus|cincinnati|cleveland|indianapolis|new orleans|salt lake city|provo|honolulu|anchorage|palo alto|menlo park|mountain view|sunnyvale|foster city|burlingame|bastrop|hawthorne|el segundo|long beach|north reading|charleston|washington dc|washington, d\.c\.)\b/i
const FOREIGN = /\b(?:canada|canadian|ontario|qu[eé]bec|british columbia|alberta|manitoba|saskatchewan|nova scotia|toronto|montr[eé]al|vancouver|ottawa|calgary|edmonton|winnipeg|united kingdom|england|scotland|wales|northern ireland|london|manchester|stoke-on-trent|edinburgh|belfast|uk|ireland|dublin|cork|germany|berlin|munich|frankfurt|france|paris|spain|madrid|barcelona|italy|milan|rome|portugal|lisbon|netherlands|amsterdam|sweden|stockholm|norway|oslo|finland|helsinki|denmark|copenhagen|switzerland|zurich|poland|warsaw|czech|prague|romania|bucharest|bulgaria|sofia|greece|athens|malta|sliema|israel|tel aviv|india|bengaluru|bangalore|hyderabad|pune|mumbai|delhi|noida|gurugram|gurgaon|chennai|singapore|china|beijing|shanghai|shenzhen|hong kong|taiwan|taipei|japan|tokyo|osaka|korea|seoul|philippines|manila|indonesia|jakarta|malaysia|kuala lumpur|thailand|bangkok|vietnam|australia|sydney|melbourne|brisbane|new zealand|auckland|mexico|brazil|brasil|s[aã]o paulo|argentina|buenos aires|colombia|bogot[aá]|chile|santiago|uruguay|costa rica|dominican republic|south africa|cape town|johannesburg|nigeria|kenya|dubai|abu dhabi|united arab emirates|saudi arabia|europe|emea|apac|latam)\b/i

export function jobGeography(job) {
  const country = String(job.country_code || job.country || '').trim()
  if (/^(?:us|usa|united states(?: of america)?)$/i.test(country)) return 'us'
  if (country && !/^(?:unknown|remote|global|worldwide)$/i.test(country)) return 'international'
  const location = String(job.location || '').normalize('NFKC').trim()
  if (!location || /^(?:remote|hybrid|distributed|in.office|on.site|anywhere|worldwide|global|[-—])$/i.test(location)) return 'unspecified'
  if (US_EXCLUDED.test(location)) return 'international'
  if (US_EXPLICIT.test(location)) return 'us'
  const segments = location.split(/\s*(?:\||;|•|\bor\b)\s*/i)
  let foreign = false
  for (const segment of segments) {
    // A stated US state disambiguates shared city names (Ontario, CA;
    // London, KY). A foreign country still overrides it.
    const foreignCountry = /\b(?:canada|united kingdom|england|scotland|uk|india|germany|france|australia|japan|china)\b/i.test(segment)
    if (!foreignCountry && US_STATE_CODE.test(segment) && !/^remote\s*[,/-]/i.test(segment)) return 'us'
    if (/\bnew mexico\b/i.test(segment)) return 'us'
    if (FOREIGN.test(segment)) { foreign = true; continue }
    if (US_STATES.test(segment) || US_CITIES.test(segment)) return 'us'
    // Remote, CA and a bare country/state abbreviation are ambiguous.
    if (US_STATE_CODE.test(segment) && !/^remote\s*[,/-]/i.test(segment)) return 'us'
  }
  return foreign ? 'international' : 'unspecified'
}

export function filterJobs(rows, options = {}, applied = (job) => job.applied === true) {
  const opts = { ...DEFAULT_JOB_FILTERS, ...options }
  const search = String(opts.search || '').trim().toLowerCase()
  return rows.filter((job) => {
    if (opts.status === 'active' && job.is_active !== true) return false
    if (['closed', 'inactive'].includes(opts.status) && job.is_active !== false) return false
    if (opts.status === 'applied' && !applied(job)) return false
    if (!opts.includeInternational && jobGeography(job) !== 'us') return false
    if (opts.company && !String(job.company || job.team || '').toLowerCase().includes(opts.company.toLowerCase())) return false
    if (opts.location && !String(job.location || '').toLowerCase().includes(opts.location.toLowerCase())) return false
    if (opts.league && job.league !== opts.league) return false
    if (opts.source && (job.ats || job.platform) !== opts.source) return false
    if (opts.remoteOnly && !/remote/i.test(job.location || '')) return false
    if (search && ![job.title, job.company, job.team, job.location].join(' ').toLowerCase().includes(search)) return false
    return true
  }).sort((a, b) => compareJobs(a, b, opts.sort))
}

export function initialVisibleCount(selection, total = Infinity) {
  return Math.min(total, selection === 'all' ? 200 : RESULT_COUNTS.includes(Number(selection)) ? Number(selection) : 100)
}
export function nextVisibleCount(current, selection, total) {
  return Math.min(total, current + (selection === 'all' ? 200 : Number(selection) || 100))
}

export function safeJobUrl(value) {
  try { const url = new URL(value); return ['https:', 'http:'].includes(url.protocol) ? url.href : null } catch { return null }
}

// Bounded keyset pagination. Metadata only; descriptions are loaded on demand.
// Rows beyond the first PostgREST page participate in filters and sorting.
export async function fetchAllJobRows({ url, key, table, columns, signal, fetchImpl = fetch, onProgress }) {
  if (!['jobs', 'robotics_jobs', 'tech_jobs', 'team_jobs'].includes(table)) throw new Error('Unknown jobs table')
  if (!url || !key) throw new Error('Jobs data is not configured')
  const rows = [], ids = new Set(), controller = new AbortController()
  const cancel = () => controller.abort()
  signal?.addEventListener('abort', cancel, { once: true })
  if (signal?.aborted) cancel()
  const timer = setTimeout(cancel, 180000)
  let cursor = null
  try {
    for (let page = 0; page < 100; page++) {
      const params = new URLSearchParams({ select: columns, order: 'id.asc', limit: '1000' })
      if (cursor !== null) params.set('id', `gt.${cursor}`)
      const response = await fetchImpl(`${url.replace(/\/+$/, '')}/rest/v1/${table}?${params}`, {
        headers: { apikey: key, Authorization: `Bearer ${key}` }, signal: controller.signal,
      })
      if (!response.ok) throw new Error(`Jobs data request failed (HTTP ${response.status})`)
      const batch = await response.json()
      if (!Array.isArray(batch)) throw new Error('Jobs data returned an unexpected response')
      for (const job of batch) {
        if (job.id == null) throw new Error('Jobs data is missing a pagination ID')
        if (!ids.has(job.id)) { rows.push(job); ids.add(job.id) }
      }
      onProgress?.(rows.length)
      if (batch.length === 0) return rows
      const next = batch.at(-1).id
      if (String(next) === String(cursor)) throw new Error('Jobs pagination stopped advancing')
      cursor = next
    }
    throw new Error('Jobs data exceeded the pagination safety limit; refresh or narrow the source')
  } finally {
    clearTimeout(timer)
    signal?.removeEventListener('abort', cancel)
  }
}
