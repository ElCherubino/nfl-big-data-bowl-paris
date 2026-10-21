import React, {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {loadCatalog, loadSeason, loadGame} from './data/siteData.js';
import CoachDashboard from './features/coach/CoachDashboard.jsx';
import BroadcasterDashboard from './features/broadcaster/BroadcasterDashboard.jsx';
import './style.css';

function readRoute() {
  const q = new URLSearchParams(location.search);
  return {entry:q.get('entry') || 'coach', game:q.get('game') || '', play:q.get('play') || '', back:q.get('back') || '', view:q.get('view') || 'plays'};
}
function App() {
  const [route,setRoute] = useState(readRoute);
  const [catalog,setCatalog] = useState(null);
  const [season,setSeason] = useState(null);
  const [bundle,setBundle] = useState(null);
  const [error,setError] = useState(null);
  const [gameError,setGameError] = useState(null);
  const [retry,setRetry] = useState(0);
  const [loadingGame,setLoadingGame] = useState(false);
  useEffect(()=> { const pop=()=>setRoute(readRoute()); addEventListener('popstate',pop); return ()=>removeEventListener('popstate',pop); },[]);
  function navigate(patch, reset=false) {
    const next = reset ? {entry:'coach',game:'',play:'',back:'',view:'plays',...patch} : {...route,...patch};
    const url=new URL(location.href); url.search='';
    for(const [key,value] of Object.entries(next)) if(value) url.searchParams.set(key,value);
    history.pushState({},'',url); setRoute(next);
  }
  useEffect(()=> {
    const controller=new AbortController(); let active=true; setError(null);
    Promise.all([loadCatalog({signal:controller.signal}),loadSeason({signal:controller.signal})]).then(([c,s])=>{if(active){setCatalog(c);setSeason(s);}}).catch(e=>{if(active&&e.name!=='AbortError')setError(e);});
    return ()=>{active=false;controller.abort();};
  },[retry]);
  useEffect(()=> {
    const controller=new AbortController(); let active=true; setBundle(null);setGameError(null);setLoadingGame(false);
    if(route.entry!=='coach' || !catalog || !route.game || !catalog.games.some(g=>g.gameId===route.game)) return ()=>controller.abort();
    setLoadingGame(true);
    loadGame(route.game,{signal:controller.signal}).then(data=>{if(active){setBundle(data);setLoadingGame(false);}}).catch(e=>{if(active&&e.name!=='AbortError'){setGameError(e);setLoadingGame(false);}});
    return ()=>{active=false;controller.abort();};
  },[catalog,route.entry,route.game,retry]);
  const invalid = !['coach','broadcaster'].includes(route.entry) ? 'Unknown entry.' : !['plays','match','season'].includes(route.view) ? 'Unknown view.' : route.game && catalog && !catalog.games.some(g=>g.gameId===route.game) ? 'This game is not in the publication.' : (route.play||route.back)&&!route.game ? 'This selection requires a game.' : bundle?.gameId===route.game && route.play && !bundle.plays.some(p=>p.playId===route.play) ? 'This play is not in the selected game.' : bundle?.gameId===route.game && route.back && !bundle.plays.some(p=>p.observations?.some(o=>o.nflId===route.back)) ? 'This back is not observed in this game.' : bundle?.gameId===route.game && route.play && route.back && !bundle.plays.find(p=>p.playId===route.play)?.observations?.some(o=>o.nflId===route.back) ? 'This back is not observed on the selected play.' : null;
  const manifest=catalog?.manifest;
  return <div className="app-shell"><a className="skip-link" href="#workspace">Skip to content</a><header className="masthead"><a className="wordmark" href="?entry=coach">CHECK<span>DOWN</span><small>THE OUTLET UNDER PRESSURE</small></a><nav aria-label="Audience"><button aria-current={route.entry==='coach'?'page':undefined} onClick={()=>navigate({entry:'coach'})}>Coach <small>& scout</small></button><button aria-current={route.entry==='broadcaster'?'page':undefined} onClick={()=>navigate({entry:'broadcaster',game:'',play:'',back:''})}>Broadcaster</button></nav><span className="period">2021 · weeks 1–8</span></header><main id="workspace"><div className="eyebrow">NFL TRACKING INTELLIGENCE <span>HISTORICAL · 8 WEEKS</span></div><div className="hero"><div><h1>{route.entry==='broadcaster'?<>THE NUMBERS.<br/><em>THE STORY.</em></>:<>UNDER PRESSURE.<br/><em>AN OUTLET?</em></>}</h1><p>{route.entry==='broadcaster'?'Traceable observations to prepare your commentary.':'Review the safety valves. Size up the backs. Prepare the next film session.'}</p></div><div className="hero-note"><span>THE QUESTION ON THE FIELD</span><strong>Was the RB open as a safety valve when pressure reached the QB?</strong></div></div>{error?<div className="state error" role="alert"><h2>Publication unavailable</h2><p>{error.message}</p><button onClick={()=>setRetry(x=>x+1)}>Retry</button></div>:!catalog||!season?<div className="state" role="status">Loading the verified publication…</div>:invalid?<div className="state error" role="alert"><h2>Invalid selection</h2><p>{invalid}</p><button onClick={()=>navigate({},true)}>Back to catalogue</button></div>:route.entry==='broadcaster'?<BroadcasterDashboard season={season}/>:<CoachDashboard catalog={catalog} season={season} bundle={bundle?.gameId===route.game?bundle:null} route={route} navigate={navigate} loadingGame={loadingGame} gameError={gameError} retry={()=>setRetry(x=>x+1)}/>}<footer><b>CHECKDOWN</b><span>Historical review tool · descriptive association, no causal claim.</span>{manifest&&<details><summary>Publication traceability</summary><p>Generation: {manifest.generationId}<br/>Calculation: {manifest.calculationVersion}<br/>Published: {manifest.generatedAt}<br/>Sources: {manifest.sourceFingerprint}</p></details>}</footer></main></div>;
}
createRoot(document.getElementById('root')).render(<App/>);
