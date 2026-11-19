// A sports-team job is shown under its team(s), with the owner's name beneath. Run: node sports_teams/board/test_team_cards.mjs
import assert from 'node:assert/strict'
import { filterJobs, jobTeams } from './job-board-core.mjs'
import { jobCardMarkup } from './standalone-ui.mjs'

const base = { is_active: true, location: 'Toronto, Ontario, Canada', url: 'https://example.com/1', posted_at: '2026-11-18' }
const canadiens = { ...base, id: 1, title: 'Analyst', team: 'Montreal Canadiens', league: 'NHL', company: 'Groupe CH', logo_url: 'https://logos.example/mtl.png', teams: null }
const mlse = { ...base, id: 2, title: 'Software Engineer', team: 'Toronto Raptors', league: 'NBA', company: 'Maple Leaf Sports & Entertainment', logo_url: 'https://logos.example/tor.png',
  teams: [{ league: 'NBA', team: 'Toronto Raptors', logo: 'https://logos.example/tor.png' }, { league: 'NHL', team: 'Toronto Maple Leafs', logo: 'https://logos.example/tml.png' }] }
const kraken = { ...base, id: 3, title: 'Usher', team: 'Seattle Kraken', league: 'NHL', company: 'Seattle Kraken', logo_url: 'https://logos.example/sea.png' }
const robotics = { ...base, id: 4, title: 'Engineer', company: 'Waymo' }
const jobs = [canadiens, mlse, kraken, robotics]
const all = { includeInternational: true, status: 'all' }

// one stored job, two teams
assert.deepEqual(jobTeams(mlse).map((t) => t.team), ['Toronto Raptors', 'Toronto Maple Leafs'])
assert.deepEqual(jobTeams(canadiens), [{ league: 'NHL', team: 'Montreal Canadiens', logo: 'https://logos.example/mtl.png' }])
assert.deepEqual(jobTeams(robotics), [])

// the league filter finds the two-team job under both leagues, and only once in the list
assert.deepEqual(filterJobs(jobs, { ...all, league: 'NHL' }).map((j) => j.id).sort(), [1, 2, 3])
assert.deepEqual(filterJobs(jobs, { ...all, league: 'NBA' }).map((j) => j.id), [2])
assert.equal(filterJobs(jobs, all).filter((j) => j.id === 2).length, 1)
// searching either team or the owner finds it
for (const word of ['maple leafs', 'raptors', 'maple leaf sports']) assert.deepEqual(filterJobs(jobs, { ...all, search: word }).map((j) => j.id), [2], word)
assert.deepEqual(filterJobs(jobs, { ...all, search: 'groupe ch' }).map((j) => j.id), [1])
// "Team A-Z" sorts by the team shown, not by the owner
assert.deepEqual(filterJobs(jobs, { ...all, sort: 'company' }).map((j) => j.team || j.company), ['Montreal Canadiens', 'Seattle Kraken', 'Toronto Raptors', 'Waymo'])

// cards
const one = jobCardMarkup(canadiens, { logoUrl: canadiens.logo_url })
assert.match(one, /<span class="job-company">Montreal Canadiens<\/span><span class="job-owner">Groupe CH<\/span>/)
assert.equal((one.match(/class="job-logo"/g) || []).length, 1)
assert.match(one, /mtl\.png/)
const two = jobCardMarkup(mlse, { logoUrl: mlse.logo_url })
assert.match(two, /<span class="job-company">Toronto Raptors \/ Toronto Maple Leafs<\/span><span class="job-owner">Maple Leaf Sports &amp; Entertainment<\/span>/)
assert.equal((two.match(/class="job-logo"/g) || []).length, 2)
assert.match(two, /tor\.png/); assert.match(two, /tml\.png/)
const own = jobCardMarkup(kraken, { logoUrl: kraken.logo_url })
assert.match(own, /<span class="job-company">Seattle Kraken<\/span><h2/)          // no second line when the site names the team
assert.doesNotMatch(own, /job-owner/)
const other = jobCardMarkup(robotics, {})
assert.match(other, /<span class="job-company">Waymo<\/span><h2/)                  // other boards are unchanged
assert.doesNotMatch(other, /job-owner|job-logos/)
console.log('team card checks passed: 4 cards, league filter, search, sort')
