// Node DOM simulation: no browser, networking, scraper runs or real application writes.
import fs from 'node:fs/promises'
import path from 'node:path'
import assert from 'node:assert/strict'
import {createRequire} from 'node:module'
import {pathToFileURL} from 'node:url'
const root=process.env.JOBS_UI_ROOT || 'D:/abet_ops/jobs_scrapers/ui', next=process.env.SPORTSBOOK_FRONTEND_ROOT || 'D:/abet/sportsbook-jobs-dashboard', dash=process.env.ABET_DASHBOARD_ROOT || 'D:/abet_ops/abet-dashboard'
const require=createRequire(process.env.JOBS_UI_DOM_PACKAGE || 'E:/abet/.cache/tmp/opencode/jobs-ui-dom/package.json')
const {JSDOM}=require('jsdom')
const ui=await import(pathToFileURL(root+'/standalone-ui.mjs'))
const core=await import(pathToFileURL(root+'/job-board-core.mjs'))
const css=await fs.readFile(root+'/standalone.css','utf8')
for(const target of ['robotics','tech','teams'])assert.equal(await fs.readFile(`${root}/${target}/standalone.css`,'utf8'),css)
assert.equal(await fs.readFile(`${next}/app/standalone.css`,'utf8'),css)
assert(css.includes('grid-template-rows:repeat(2,34px)')&&css.includes('grid-auto-flow:column')&&css.includes('overflow-x:auto'))
const fakeJobs=Array.from({length:230},(_,index)=>({id:index+1,company:index%2?'OpenAI':'Zoox',team:index%2?'Team B':'Team A',league:'NBA',title:`Role ${index+1}`,url:`https://example.org/job/${index+1}`,location:'Tempe, AZ',posted_at:`2026-11-${String(10-index%8).padStart(2,'0')}`,is_active:true,ats:'greenhouse'}))
fakeJobs.push({...fakeJobs[0],id:991,title:'Foreign only',url:'https://example.org/foreign',location:'London, UK'})
fakeJobs.push({...fakeJobs[0],id:992,title:'Closed only',url:'https://example.org/closed',is_active:false})
fakeJobs.push({...fakeJobs[0],id:993,title:'Undated last',url:'https://example.org/undated',posted_at:null})
const report={checked_at:new Date().toISOString(),browser_visual_check:false,static:[],react:{}}
const fakeResponse=(data)=>({ok:true,status:200,json:async()=>data})
let descCalls=0
const savedFetch=globalThis.fetch
globalThis.fetch=async()=>{descCalls++;return fakeResponse([{description:'<p>Verified description &amp; details.</p>'}])}
const settle=()=>new Promise(resolve=>setTimeout(resolve,30))
try{
 for(const [industry,file,title] of [['robotics','index.html','Robotics Jobs'],['tech','index.html','Tech Jobs'],['teams','live.html','Sports Teams Jobs']]){
  const html=await fs.readFile(`${root}/${industry}/${file}`,'utf8')
  assert(!html.includes('<table'),industry+' still contains a table')
  const dom=new JSDOM(html,{url:`https://example.org/${industry}/`,runScripts:'outside-only'}), w=dom.window
  let scrollCalls=0, applicationWrites=0
  Object.assign(w,core,ui,{fetchAllJobRows:async()=>fakeJobs,fetch:async(url,options={})=>{
   if(options.method){applicationWrites++;return fakeResponse([])}
   if(String(url).includes('applications?'))return fakeResponse([])
   if(String(url).includes('health'))return fakeResponse({status:'healthy',latest_manifest:{totals:{successful:1,providers:1}}})
   throw Error('Unexpected network request '+url)
  },ResizeObserver:class{observe(){} disconnect(){}},IntersectionObserver:class{observe(){} disconnect(){}},matchMedia:()=>({matches:false})})
  w.HTMLElement.prototype.scrollBy=function(){scrollCalls++}
  const source=html.match(/<script type="module">([\s\S]*?)<\/script>/)[1].replace(/^import .*?;\s*$/gm,'')
  w.eval(source)
  await settle()
  const d=w.document
  assert.equal(d.querySelector('h1').textContent,title)
  assert.equal(d.querySelector('.abet-wordmark').getAttribute('aria-label'),'ABET dashboard')
  assert.equal(d.querySelectorAll('.job-card').length,100,industry+' initial cards')
  assert.equal(d.querySelectorAll('.job-title').length,100)
  assert(!d.querySelector('.job-list').textContent.includes('Foreign only'))
  if(industry==='robotics'){const off=d.getElementById('offtopic');off.checked=false;off.dispatchEvent(new w.Event('input',{bubbles:true}))}
  const summary=d.querySelector('.board-overview>summary');summary.click();assert.equal(d.querySelector('.board-overview').open,false);summary.click();assert(d.querySelector('.board-overview').open)
  d.getElementById('companies-right').click();assert.equal(scrollCalls,1)
  const limit=d.getElementById('limit');limit.value='200';limit.dispatchEvent(new w.Event(industry==='teams'?'change':'input',{bubbles:true}));assert.equal(d.querySelectorAll('.job-card').length,200)
  limit.value='all';limit.dispatchEvent(new w.Event(industry==='teams'?'change':'input',{bubbles:true}));d.getElementById('more').click();assert.equal(d.querySelectorAll('.job-card').length,231)
  // Robotics retains its established off-topic employer filter (OpenAI).
  const q=d.getElementById('q');q.value='Undated last';q.dispatchEvent(new w.Event('input',{bubbles:true}));assert.equal(d.querySelectorAll('.job-card').length,1)
  const detail=d.querySelector('.job-details');detail.open=true;await settle();assert(detail.querySelector('.job-description').textContent.includes('Verified description & details.'))
  // Application controls exercise only the mocked endpoints/localStorage.
  d.querySelector('.apply-btn').click();await settle();assert.equal(d.querySelector('.apply-btn').getAttribute('aria-pressed'),'true')
  report.static.push({industry,header:true,sharedCards:true,collapse:true,horizontalScroll:true,resultCounts:true,description:true,applicationControl:true,mockedApplicationWrites:applicationWrites})
  dom.window.close()
 }
}finally{globalThis.fetch=savedFetch}

const dashRequire=createRequire(dash+'/package.json'),{build}=dashRequire('esbuild'),React=dashRequire('react'),{renderToStaticMarkup}=dashRequire('react-dom/server')
const cache=dash+'/node_modules/.cache/jobs-presentation-proof';await fs.mkdir(cache,{recursive:true})
async function component(file){const outfile=cache+'/'+file+'.mjs';await build({absWorkingDir:dash,entryPoints:[next+'/app/components/'+file+'.tsx'],outfile,bundle:true,format:'esm',platform:'node',jsx:'automatic',packages:'external',logLevel:'silent'});return(await import(pathToFileURL(outfile))).default}
const [Header,Overview,Jobs]=await Promise.all(['StandaloneHeader','BoardOverview','JobsBoard'].map(component))
const header=renderToStaticMarkup(React.createElement(Header));assert(header.includes('Sportsbook Jobs')&&header.includes('abet-wordmark')&&!header.includes('SB-JOBS'))
const overview=renderToStaticMarkup(React.createElement(Overview,{companies:[['Zoox',10],['OpenAI',12]],total:22,active:20,inactive:2,applied:1,selected:'ALL',onSelect:()=>{}}))
assert(overview.includes('board-overview')&&overview.includes('company-scroll')&&overview.includes('Scroll companies right'))
const cards=renderToStaticMarkup(React.createElement(Jobs,{jobs:fakeJobs,selectedCompany:'Zoox'}));assert(cards.includes('job-card-heading')&&cards.includes('job-details'));const cardDom=new JSDOM(cards);assert([...cardDom.window.document.querySelectorAll('.job-company')].every(el=>el.textContent==='Zoox'));cardDom.window.close()
const reactDom=new JSDOM('<div id="app"></div>',{url:'https://example.org/sportsbook/'})
globalThis.window=reactDom.window;globalThis.document=reactDom.window.document;globalThis.IS_REACT_ACT_ENVIRONMENT=true
reactDom.window.matchMedia=()=>({matches:false})
let reactScrolls=0;reactDom.window.HTMLElement.prototype.scrollBy=function(){reactScrolls++}
const {createRoot}=dashRequire('react-dom/client'),act=React.act || dashRequire('react-dom/test-utils').act
function Harness(){const [selected,setSelected]=React.useState('ALL');return React.createElement(React.Fragment,null,React.createElement(Overview,{companies:[['Zoox',116],['OpenAI',115]],total:231,active:231,inactive:0,applied:0,selected,onSelect:setSelected}),React.createElement(Jobs,{jobs:fakeJobs,selectedCompany:selected,onCompanySelect:setSelected}))}
const reactRoot=createRoot(document.getElementById('app'));await act(async()=>reactRoot.render(React.createElement(Harness)))
await act(async()=>[...document.querySelectorAll('.company-pill')].find(el=>el.textContent.includes('OpenAI')).click())
assert([...document.querySelectorAll('.job-company')].every(el=>el.textContent==='OpenAI'))
assert.equal(document.querySelector('select[aria-label="Company"]').value,'OpenAI')
await act(async()=>document.querySelector('.board-overview>summary').click());assert(!document.querySelector('.board-overview').open)
await act(async()=>document.querySelector('.board-overview>summary').click())
await act(async()=>document.querySelector('[aria-label="Scroll companies right"]').click());assert.equal(reactScrolls,1)
await act(async()=>reactRoot.unmount());reactDom.window.close();delete globalThis.window;delete globalThis.document;delete globalThis.IS_REACT_ACT_ENVIRONMENT
const safeCard=ui.jobCardMarkup({...fakeJobs[0],title:'<img src=x onerror=alert(1)>',url:'javascript:alert(1)'})
assert(safeCard.includes('&lt;img'));assert(!safeCard.includes('href="javascript:'))
report.react={header:true,summary:true,sharedCards:true,controlledCompanyFilter:true,companyClick:true,summaryCollapse:true,horizontalScroll:true};report.styles_identical=true;report.descriptionCalls=descCalls
await fs.writeFile(root+'/presentation-dom-proof.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2))
