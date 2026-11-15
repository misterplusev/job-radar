// One cloud browser, eight sequential public pages, GET/HEAD/OPTIONS only.
// No agents, no local-machine execution, no app writes, always close in finally.
import fs from 'node:fs/promises';
import os from 'node:os';
import assert from 'node:assert/strict';
import { chromium } from 'playwright';

function guardBeforeBrowser() {
  if (process.env.GITHUB_ACTIONS !== 'true' || process.env.RUNNER_ENVIRONMENT !== 'github-hosted' || process.platform !== 'linux')
    throw new Error('Only the authorized GitHub-hosted cloud proof may start this browser');
  if (process.env.CLOUD_PROOF_STOP === '1' || 1-os.freemem()/os.totalmem() > .85)
    throw new Error('Cloud proof stop or memory guard');
}
const modules = [
  ['robotics','robotics-jobs','https://misterplusev.github.io/robotics-jobradar-board/'],
  ['tech','tech-jobs','https://misterplusev.github.io/jobradar-tech-board/'],
  ['teams','teams-jobs','https://misterplusev.github.io/job-radar/'],
  ['sportsbook','jobs-browser','https://sportsbook-jobs-dashboard.vercel.app/'],
];
await fs.mkdir('proof/screenshots', {recursive:true});
const report = {observed_at:new Date().toISOString(), runtime:'GitHub-hosted cloud browser', mocked:false, pages:[]};
guardBeforeBrowser();
const browser = await chromium.launch({headless:true});
try {
  for (const [module, tab, standalone] of modules) {
    for (const [kind,url] of [['standalone',standalone],['dashboard',`https://abet-dashboard.vercel.app/?section=jobs&tab=${tab}`]]) {
      guardBeforeBrowser();
      const context = await browser.newContext({viewport:{width:1440,height:1080}, reducedMotion:'reduce',timezoneId:'America/Los_Angeles'});
      await context.route('**/*', route => ['GET','HEAD','OPTIONS'].includes(route.request().method()) ? route.continue() : route.abort());
      const page = await context.newPage();
      const item = {module,kind,url,errors:[],data_responses:[]};
      page.on('pageerror', error => item.errors.push(error.message.slice(0,240)));
      page.on('response', response => {
        const u=new URL(response.url());
        if (u.hostname.endsWith('.supabase.co') && u.pathname.startsWith('/rest/v1/'))
          item.data_responses.push({table:u.pathname.split('/').at(-1),status:response.status()});
      });
      try {
        const response=await page.goto(url,{waitUntil:'domcontentloaded',timeout:45000});
        item.http=response.status();
        await page.locator('.job-card').first().waitFor({state:'visible',timeout:180000});
        item.heading=await page.locator('.board-heading h1').first().innerText();
        item.cards=await page.locator('.job-card').count();
        assert(item.cards>0);
        const legacy=kind==='standalone' && module!=='sportsbook';
        const status=legacy?page.locator(module==='teams'?'#status':'#st'):page.getByLabel('Status',{exact:true});
        const sort=legacy?page.locator('#sort'):page.getByLabel('Sort',{exact:true});
        const limit=legacy?page.locator('#limit'):page.getByLabel('Initial result count',{exact:true});
        assert.equal(await status.inputValue(),'active');
        assert.equal(await sort.inputValue(),'newest');
        assert.equal(await limit.inputValue(),'100');
        const international=legacy?page.locator('#international'):page.getByLabel(/Include international/);
        assert.equal(await international.isChecked(),false);
        item.defaults={active:true,newest:true,us:true,limit:100};
        item.first_jobs=await page.locator('.job-card').evaluateAll(cards => cards.slice(0,3).map(card=>({
          title:card.querySelector('.job-title')?.textContent,
          href:card.querySelector('a[href^="http"]')?.href,
          logos:[...card.querySelectorAll('img')].map(img=>({loaded:img.complete&&img.naturalWidth>0,src:img.currentSrc}))
        })));
        assert(item.first_jobs.every(job=>/^https?:\/\//.test(job.href)));
        await page.screenshot({path:`proof/screenshots/${module}-${kind}.png`});
        const previous=item.cards;
        await limit.selectOption('200');
        await page.waitForTimeout(200);
        item.cards_200=await page.locator('.job-card').count();
        assert(item.cards_200>=previous);
        await limit.selectOption('100');
        const overview=page.locator('.board-overview');
        await overview.locator('summary').first().click();
        assert.equal(await overview.getAttribute('open'),null);
        await overview.locator('summary').first().click();
        await international.check();
        assert(await international.isChecked());
        await international.uncheck();
        await sort.selectOption('oldest');
        assert.equal(await sort.inputValue(),'oldest');
        await sort.selectOption('newest');
        await status.selectOption('all');
        assert.equal(await status.inputValue(),'all');
        await status.selectOption('active');
        const detail=page.locator('.job-details summary').first();
        if(await detail.count()) { await detail.click(); await page.waitForTimeout(1000); }
        item.controls_passed=true;
        assert.equal(item.errors.length,0,item.errors.join('\n'));
        assert(!item.data_responses.some(r=>r.status>=400), 'A database request failed');
        item.passed=true;
      } catch (error) {
        item.passed=false; item.failure=error.message.slice(0,700);
        item.visible_text=(await page.locator('body').innerText().catch(()=>'' )).slice(0,1800);
        await page.screenshot({path:`proof/screenshots/${module}-${kind}-failed.png`}).catch(()=>{});
      } finally { await context.close(); }
      report.pages.push(item);
      await fs.writeFile('proof/browser-proof.json',JSON.stringify(report,null,2));
      console.log(JSON.stringify({module,kind,passed:item.passed,cards:item.cards,failure:item.failure}));
    }
  }
} finally { await browser.close(); }
if(report.pages.length!==8 || report.pages.some(page=>!page.passed)) process.exitCode=1;
