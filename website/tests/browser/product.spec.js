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

test('coach selects real game and play, stops at pressure, resumes observed trajectory',async({page})=>{
 await start(page); await page.getByRole('combobox',{name:'Match',exact:true}).selectOption(game.gameId);
 await page.getByLabel('Rechercher un jeu').fill(play.playId);
 await page.getByRole('button',{name:'Revoir le jeu'}).click();
 await expect(page.getByRole('img',{name:/Terrain à/})).toBeVisible();
 const timeline=page.getByRole('slider',{name:'Frame du rejeu'});
 await expect(timeline).toHaveValue('0');
 await page.getByRole('button',{name:'▶ Lire',exact:true}).click();
 await expect(timeline).toHaveValue(String(pressureIndex),{timeout:20000});
 await expect(page.getByRole('button',{name:'▶ Lire',exact:true})).toBeVisible();
 await expect(page.getByRole('img',{name:new RegExp(`frame ${play.events.pressureFrameId}\\.`)})).toBeVisible();
 await page.getByRole('button',{name:'▶ Lire',exact:true}).click();
 await expect.poll(async()=>Number(await timeline.inputValue())).toBeGreaterThan(pressureIndex);
 await page.getByRole('button',{name:'À la pression'}).click();
 await expect(timeline).toHaveValue(String(pressureIndex));
 await expect(page.locator('.replay-checks').first()).toContainText('En route');
});

test('match back evidence filter can be removed and browser history restores views',async({page})=>{
 await start(page,`?game=${game.gameId}&view=match`);
 await page.getByRole('button',{name:'Voir ses jeux'}).first().click();
 await expect(page.getByRole('button',{name:/Retirer le filtre/})).toBeVisible();
 await page.getByRole('button',{name:/Retirer le filtre/}).click();
 await expect(page.getByRole('button',{name:/Retirer le filtre/})).toHaveCount(0);
 await page.goBack(); await expect(page.getByRole('button',{name:/Retirer le filtre/})).toBeVisible();
 await page.goForward(); await expect(page.getByRole('button',{name:/Retirer le filtre/})).toHaveCount(0);
});

test('scout filters retain published rank and denominator',async({page})=>{
 const season=read(manifest.resources.seasonRb).data;
 const row=season.rows.find(r=>r.eligible)||season.rows[0];
 await start(page,'?view=season');
 await page.getByLabel('Nom ou identifiant').fill(row.nflId);
 const tr=page.getByRole('row').filter({has:page.getByText(row.displayName,{exact:true})});
 const cells=await tr.getByRole('cell').allTextContents();
 expect(cells[0]).toContain(row.eligible?String(row.rank):'Non classé');
 expect(cells[2]).toBe(String(row.counts.evaluatedPlays));
 await page.getByLabel('Équipe observée').selectOption(row.teams[0]);
 expect(await tr.getByRole('cell').allTextContents()).toEqual(cells);
});

test('broadcaster requests season only and offers no replay',async({page})=>{
 const requests=[];page.on('request',r=>requests.push(r.url()));
 await start(page,'?entry=broadcaster');
 await expect(page.getByRole('heading',{name:/LE RÉCIT/})).toBeVisible();
 await expect(page.getByRole('alert')).toHaveCount(0);
 await expect(page.locator('table').first()).toBeVisible();
 expect(requests.filter(u=>/game_\d+\.json/.test(u))).toEqual([]);
 await expect(page.getByRole('slider')).toHaveCount(0);
});

test('invalid linked selection recovers to catalogue',async({page})=>{
 await start(page,'?game=absent&play=123');
 await expect(page.getByRole('alert')).toContainText('Sélection invalide');
 await page.getByRole('button',{name:'Revenir au catalogue'}).click();
 await expect(page.getByRole('combobox',{name:'Match',exact:true})).toBeVisible();
 await expect(page.getByRole('alert')).toHaveCount(0);
});

for(const kind of ['missing','schema','generation','network']) test(`explicit ${kind} publication error without invented metrics`,async({page})=>{
 if(kind==='missing'||kind==='network') await page.route('**/data/manifest.json',route=>kind==='network'?route.abort():route.fulfill({status:404,body:'absent'}));
 if(kind==='schema') await page.route('**/data/manifest.json',route=>route.fulfill({json:{...manifest,schemaVersion:'99.0.0'}}));
 if(kind==='generation') await page.route('**/season_rb.json',async route=>{const response=await route.fetch();await route.fulfill({json:{...await response.json(),generationId:'stale-test-generation'}});});
 await start(page);
 await expect(page.getByRole('alert')).toContainText('Publication indisponible');
 await expect(page.getByRole('alert')).toContainText({missing:'Publication absente',schema:'incompatible',generation:'générations différentes',network:'Impossible de charger'}[kind]);
 await expect(page.locator('.rate-highlight')).toHaveCount(0);
});

test('mobile keyboard opens a real replay with textual alternative',async({page})=>{
 await page.setViewportSize({width:390,height:844});
 await start(page,`?game=${game.gameId}&play=${play.playId}`);
 await expect(page.getByRole('img',{name:/Terrain à/})).toBeVisible();
 const button=page.getByRole('button',{name:'À la pression'});
 await button.focus();await page.keyboard.press('Enter');
 await expect(page.getByRole('slider')).toHaveValue(String(pressureIndex));
 await page.getByText('Alternative textuelle : positions à cette frame').click();
 await expect(page.locator('.replay-text table')).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
});

test('capture five real audit plays from published tracking',async({page})=>{
 test.skip(!bundle.plays.some(p=>p.playId==='4560'),'Audit match not in this publication');
 for(const id of ['4560','2279','97','349','1368']){
  await start(page,`?game=${game.gameId}&play=${id}`);
  const field=page.getByRole('img',{name:/Terrain à/}); await expect(field).toBeVisible();
  const pressure=page.getByRole('button',{name:'À la pression'});if(await pressure.isEnabled()) await pressure.click();
  await page.locator('#selected-replay').screenshot({path:`test-results/audit-${game.gameId}-${id}.png`});
 }
});

test('no-pressure replay exposes published current checks without counting opportunity',async({page})=>{
 const noPressure=bundle.plays.find(p=>p.playId==='97')||bundle.plays.find(p=>p.pressure.status==='none'&&p.frames.length>1&&p.frames[0].rbStates.length);
 await start(page,`?game=${game.gameId}&play=${noPressure.playId}`);
 await page.getByText('Conditions à l’instant affiché',{exact:true}).click();
 const table=page.locator('.replay-current-checks table');
 await expect(table).toBeVisible();
 await expect(table.getByRole('row')).toHaveCount(6);
 const state=noPressure.frames[0].rbStates[0];
 await expect(table).toContainText(state.checks.routeRunner.passed?'Oui':'Non');
 await expect(page.getByRole('region',{name:'Mesures publiées à la pression'})).toContainText('Aucune pression détectée → non compté.');
 await page.getByRole('button',{name:'Frame →',exact:true}).click();
 await expect(page.getByRole('slider')).toHaveValue('1');
 await expect(page.locator('.replay-current')).toContainText(`${noPressure.frames[1].timeS.toFixed(1)} s`);
 await expect(page.getByRole('region',{name:'Mesures publiées à la pression'})).toContainText('Aucune pression détectée → non compté.');
});
