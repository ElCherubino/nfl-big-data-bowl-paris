import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
const folder=resolve('public/data');
const read=p=>JSON.parse(readFileSync(resolve(folder,p),'utf8'));
const manifest=read('manifest.json');
const games=read(manifest.resources.games).data;
const game=games.find(g=>g.gameId==='2021090900')||games[0];
const bundle=read(game.gameResource).data;
const play=bundle.plays.find(p=>p.pressure.status==='detected'&&p.observations.some(o=>o.counted)&&p.events.pressureFrameId<p.events.endFrameId);
const pressureIndex=play.frames.findIndex(f=>f.frameId===play.events.pressureFrameId);
const appPath=new URL(process.env.RB_BROWSER_URL||'http://127.0.0.1:4173').pathname;
const start=(page,query='')=>page.goto(`${appPath}${query}`);

test('coach selects real game and play, replay starts on its own, stops at pressure, resumes observed trajectory',async({page})=>{
 await start(page); await page.getByRole('combobox',{name:'Game',exact:true}).selectOption(game.gameId);
 await page.getByLabel('Search plays').fill(play.playId);
 await page.getByRole('button',{name:'Replay the play'}).click();
 await expect(page.getByRole('img',{name:/Field at/})).toBeVisible();
 await expect(page.getByRole('definition').first()).toBeVisible();
 const timeline=page.getByRole('slider',{name:'Replay frame'});
 await expect(timeline).toHaveValue(String(pressureIndex),{timeout:20000});
 await expect(page.getByRole('button',{name:'▶ Play',exact:true})).toBeVisible();
 await expect(page.getByRole('img',{name:new RegExp(`frame ${play.events.pressureFrameId}\\.`)})).toBeVisible();
 await page.getByRole('button',{name:'▶ Play',exact:true}).click();
 await expect.poll(async()=>Number(await timeline.inputValue())).toBeGreaterThan(pressureIndex);
 await page.getByRole('button',{name:'At pressure'}).click();
 await expect(timeline).toHaveValue(String(pressureIndex));
 await expect(page.locator('.replay-checks').first()).toContainText('Running a route');
});

test('match back evidence filter can be removed and browser history restores views',async({page})=>{
 await start(page,`?game=${game.gameId}&view=match`);
 await page.getByRole('button',{name:'View plays'}).first().click();
 await expect(page.getByRole('button',{name:/Remove filter/})).toBeVisible();
 await page.getByRole('button',{name:/Remove filter/}).click();
 await expect(page.getByRole('button',{name:/Remove filter/})).toHaveCount(0);
 await page.goBack(); await expect(page.getByRole('button',{name:/Remove filter/})).toBeVisible();
 await page.goForward(); await expect(page.getByRole('button',{name:/Remove filter/})).toHaveCount(0);
});

test('scout filters retain published rank and denominator',async({page})=>{
 const season=read(manifest.resources.seasonRb).data;
 const row=season.rows.find(r=>r.eligible)||season.rows[0];
 await start(page,'?view=season');
 await page.getByLabel('Name or ID').fill(row.nflId);
 const tr=page.getByRole('row').filter({has:page.getByText(row.displayName,{exact:true})});
 const cells=await tr.getByRole('cell').allTextContents();
 expect(cells[0]).toContain(row.eligible?String(row.rank):'Unranked');
 expect(cells[2]).toBe(String(row.counts.evaluatedPlays));
 await page.getByLabel('Observed team').selectOption(row.teams[0]);
 expect(await tr.getByRole('cell').allTextContents()).toEqual(cells);
});

test('broadcaster requests season only and offers no replay',async({page})=>{
 const requests=[];page.on('request',r=>requests.push(r.url()));
 await start(page,'?entry=broadcaster');
 await expect(page.getByRole('heading',{name:/THE STORY/})).toBeVisible();
 await expect(page.getByRole('alert')).toHaveCount(0);
 await expect(page.locator('table').first()).toBeVisible();
 expect(requests.filter(u=>/game_\d+\.json/.test(u))).toEqual([]);
 await expect(page.getByRole('slider')).toHaveCount(0);
});

test('invalid linked selection recovers to catalogue',async({page})=>{
 await start(page,'?game=absent&play=123');
 await expect(page.getByRole('alert')).toContainText('Invalid selection');
 await page.getByRole('button',{name:'Back to catalogue'}).click();
 await expect(page.getByRole('combobox',{name:'Game',exact:true})).toBeVisible();
 await expect(page.getByRole('alert')).toHaveCount(0);
});

for(const kind of ['missing','schema','generation','network']) test(`explicit ${kind} publication error without invented metrics`,async({page})=>{
 if(kind==='missing'||kind==='network') await page.route('**/data/manifest.json',route=>kind==='network'?route.abort():route.fulfill({status:404,body:'absent'}));
 if(kind==='schema') await page.route('**/data/manifest.json',route=>route.fulfill({json:{...manifest,schemaVersion:'99.0.0'}}));
 if(kind==='generation') await page.route('**/season_rb.json',async route=>{const response=await route.fetch();await route.fulfill({json:{...await response.json(),generationId:'stale-test-generation'}});});
 await start(page);
 await expect(page.getByRole('alert')).toContainText('Publication unavailable');
 await expect(page.getByRole('alert')).toContainText({missing:'Publication missing',schema:'incompatible',generation:'different generations',network:'Unable to load'}[kind]);
 await expect(page.locator('.rate-highlight')).toHaveCount(0);
});

test('mobile keyboard opens a real replay with textual alternative',async({page})=>{
 await page.setViewportSize({width:390,height:844});
 await start(page,`?game=${game.gameId}&play=${play.playId}`);
 await expect(page.getByRole('img',{name:/Field at/})).toBeVisible();
 const button=page.getByRole('button',{name:'At pressure'});
 await button.focus();await page.keyboard.press('Enter');
 await expect(page.getByRole('slider')).toHaveValue(String(pressureIndex));
 await page.getByText('Text alternative: positions at this frame').click();
 await expect(page.locator('.replay-text table')).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
});

test('capture five real audit plays from published tracking',async({page})=>{
 test.skip(!bundle.plays.some(p=>p.playId==='4560'),'Audit match not in this publication');
 for(const id of ['4560','2279','97','349','1368']){
  await start(page,`?game=${game.gameId}&play=${id}`);
  const field=page.getByRole('img',{name:/Field at/}); await expect(field).toBeVisible();
  const pressure=page.getByRole('button',{name:'At pressure'});if(await pressure.isEnabled()) await pressure.click();
  await page.locator('#selected-replay').screenshot({path:`test-results/audit-${game.gameId}-${id}.png`});
 }
});

test('no-pressure replay shows the play outcome and RB role without a pressure table',async({page})=>{
 const noPressure=bundle.plays.find(p=>p.playId==='97')||bundle.plays.find(p=>p.pressure.status==='none'&&p.observations.length&&p.passResult==='I');
 await start(page,`?game=${game.gameId}&play=${noPressure.playId}`);
 const outcome=page.locator('.play-outcome');
 await expect(outcome).toContainText('Incomplete pass');
 await expect(outcome).toContainText('RB open at pressure');
 await expect(outcome).toContainText('No pressure');
 const region=page.getByRole('region',{name:'Published measurements at pressure'});
 await expect(region).toContainText('No pressure detected on this play.');
 await expect(region.locator('table')).toHaveCount(0);
});

test('pressure table colours each threshold as met or missed',async({page})=>{
 const observation=play.observations.find(o=>o.counted);
 await start(page,`?game=${game.gameId}&play=${play.playId}&back=${observation.nflId}`);
 const rows=page.getByRole('region',{name:'Published measurements at pressure'}).locator('tbody tr');
 await expect(rows).toHaveCount(5);
 const passed=Object.values(observation.checks).filter(c=>c.passed===true).length;
 await expect(page.locator('tr.check-met')).toHaveCount(passed);
});
