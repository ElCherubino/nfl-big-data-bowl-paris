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
  const invalid = !['coach','broadcaster'].includes(route.entry) ? 'Entrée inconnue.' : !['plays','match','season'].includes(route.view) ? 'Vue inconnue.' : route.game && catalog && !catalog.games.some(g=>g.gameId===route.game) ? 'Ce match est absent de la publication.' : (route.play||route.back)&&!route.game ? 'Cette sélection nécessite un match.' : bundle?.gameId===route.game && route.play && !bundle.plays.some(p=>p.playId===route.play) ? 'Ce jeu est absent du match sélectionné.' : bundle?.gameId===route.game && route.back && !bundle.plays.some(p=>p.observations?.some(o=>o.nflId===route.back)) ? 'Ce back est absent des observations du match.' : bundle?.gameId===route.game && route.play && route.back && !bundle.plays.find(p=>p.playId===route.play)?.observations?.some(o=>o.nflId===route.back) ? 'Ce back ne participe pas aux observations du jeu sélectionné.' : null;
  const manifest=catalog?.manifest;
  return <div className="app-shell"><a className="skip-link" href="#workspace">Aller au contenu</a><header className="masthead"><a className="wordmark" href="?entry=coach">CHECK<span>DOWN</span><small>LA SOLUTION SOUS PRESSION</small></a><nav aria-label="Parcours"><button aria-current={route.entry==='coach'?'page':undefined} onClick={()=>navigate({entry:'coach'})}>Coach <small>& scout</small></button><button aria-current={route.entry==='broadcaster'?'page':undefined} onClick={()=>navigate({entry:'broadcaster',game:'',play:'',back:''})}>Broadcaster</button></nav><span className="period">2021 · semaines 1–8</span></header><main id="workspace"><div className="eyebrow">NFL TRACKING INTELLIGENCE <span>HISTORIQUE · 8 SEMAINES</span></div><div className="hero"><div><h1>{route.entry==='broadcaster'?<>LES CHIFFRES.<br/><em>LE RÉCIT.</em></>:<>SOUS PRESSION.<br/><em>UNE SOLUTION ?</em></>}</h1><p>{route.entry==='broadcaster'?'Des observations traçables pour préparer votre commentaire.':'Revoir les solutions de secours. Situer les backs. Préparer la prochaine séance vidéo.'}</p></div><div className="hero-note"><span>LA QUESTION DU TERRAIN</span><strong>Le QB avait-il un back disponible au moment de la pression ?</strong><a href="#method">Comprendre la mesure ↗</a></div></div>{error?<div className="state error" role="alert"><h2>Publication indisponible</h2><p>{error.message}</p><button onClick={()=>setRetry(x=>x+1)}>Réessayer</button></div>:!catalog||!season?<div className="state" role="status">Chargement de la publication vérifiée…</div>:invalid?<div className="state error" role="alert"><h2>Sélection invalide</h2><p>{invalid}</p><button onClick={()=>navigate({},true)}>Revenir au catalogue</button></div>:route.entry==='broadcaster'?<BroadcasterDashboard season={season}/>:<CoachDashboard catalog={catalog} season={season} bundle={bundle?.gameId===route.game?bundle:null} route={route} navigate={navigate} loadingGame={loadingGame} gameError={gameError} retry={()=>setRetry(x=>x+1)}/>}<Method manifest={manifest}/><footer><b>CHECKDOWN</b><span>Outil de revue historique · association descriptive, sans conclusion causale.</span>{manifest&&<details><summary>Traçabilité de la publication</summary><p>Génération : {manifest.generationId}<br/>Calcul : {manifest.calculationVersion}<br/>Publication : {manifest.generatedAt}<br/>Sources : {manifest.sourceFingerprint}</p></details>}</footer></main></div>;
}
function Method({manifest}) {
 const p=manifest?.parameters;
 return <section id="method" className="method panel"><div className="section-title"><span className="section-number">MÉTHODE</span><h2>Ce que l’image permet de dire.</h2></div><div className="method-grid"><div><h3>Disponibilité ≠ passe garantie</h3><p>Le dénominateur n comprend les observations joueur-jeu de RB/FB en route, sous pression détectée et avec un verdict déterminé. Les inconnues sont exclues et affichées. Un jeu à deux backs peut compter une fois par joueur ; l’attaque compte chaque jeu une seule fois.</p></div><div><h3>Un proxy géométrique</h3><p>La pression correspond à un défenseur à une distance ≤ {p?.pressureRadiusYd ?? '—'} yd du QB. Le défenseur le plus proche ne révèle pas une responsabilité de couverture. Un back doit être en route, ouvert à plus de {p?.openDistanceYd ?? '—'} yd, à portée du QB (distance strictement inférieure à {p?.maxQbDistanceYd ?? '—'} yd), au-delà de {p?.minLosProgressYd ?? '—'} yd de la ligne et orienté vers le QB avec un angle strictement inférieur à {p?.maxFacingAngleDeg ?? '—'}°. L’orientation corporelle ne mesure pas le regard. Le tracking s’arrête peu après le lancer : aucune trajectoire ou action ultérieure n’est extrapolée.</p></div><div><h3>Lire les limites</h3><p>Un back au bloc est identifié séparément. Une cible inconnue n’est pas une absence de ciblage. Ces associations ne contrôlent pas le QB, la protection ou le contexte : elles ne démontrent aucune causalité et ne sont pas une note de talent. Couverture et blitz peuvent être inconnus et leurs strates ont des effectifs limités.</p></div><div><h3>Préparer la revue, pas prédire</h3><p>2021 · semaines 1–8 seulement. Au match, les petits échantillons servent de références vidéo. En saison, le classement régularisé utilise k = {p?.shrinkageK ?? '—'} et n ≥ {p?.minSeasonN ?? '—'}. L’intervalle bootstrap à 95 % porte sur le taux brut, avec {p?.bootstrapReplicates ?? '—'} réplications et graine {p?.randomSeed ?? '—'}, jamais sur le rang.</p></div></div></section>;
}
createRoot(document.getElementById('root')).render(<App/>);
