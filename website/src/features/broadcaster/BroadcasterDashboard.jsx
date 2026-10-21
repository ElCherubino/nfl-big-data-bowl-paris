import React, {useState} from 'react';
import {ArrowUpRight, Check, Copy, Mic2} from 'lucide-react';
import {PERIOD, formatNumber, formatRate, leagueRows, quoteFor} from './broadcaster.js';
import './broadcaster.css';

export default function BroadcasterDashboard({season}) {
  const [selectedId, setSelectedId] = useState(null);
  const [copyState, setCopyState] = useState('');
  const rows = leagueRows(season?.rb);
  const reference = season?.rb?.reference;
  if (!rows || !Number.isFinite(reference.leagueAvailability)) return <section className="bc-state" role="alert"><h2>Classement indisponible.</h2><p>La table saison publiée ne permet pas d’afficher un classement vérifié.</p></section>;
  const selected = rows.find(row => row.nflId === selectedId) || rows[0];
  const quote = selected ? quoteFor(selected) : '';
  async function copyQuote() {
    try {
      await navigator.clipboard.writeText(`${quote}\nSource : génération ${season.manifest.generationId}.`);
      setCopyState('copied');
    } catch { setCopyState('failed'); }
  }
  return <div className="broadcaster">
    <section className="bc-overview" aria-labelledby="bc-title">
      <div><span className="bc-kicker"><Mic2 size={14} aria-hidden="true"/> NOTE D’ANTENNE / {PERIOD}</span><h2 id="bc-title">Best safety valves<span>Les points de sortie, en chiffres.</span></h2><p>Le classement ligue des RB et FB éligibles. Une lecture descriptive pour préparer votre prochain sujet, avec chaque chiffre rattaché à la même publication.</p></div>
      <div className="bc-reference"><span>RÉFÉRENCE LIGUE · JOUEUR-JEU</span><strong>{formatRate(reference.leagueAvailability)}</strong><p>Taux brut de disponibilité publié</p><div><span>{reference.cohortSize} backs éligibles</span><span>Minimum n = {reference.minN}</span></div></div>
    </section>
    <section className="bc-ranking" aria-labelledby="bc-ranking-title">
      <div className="bc-table-heading"><div><span className="bc-kicker">01 / CLASSEMENT LIGUE</span><h3 id="bc-ranking-title">Qui offre une sortie sous pression ?</h3></div><span className="bc-order">Ordre publié · taux régularisé décroissant</span></div>
      <div className="bc-table-scroll" tabIndex="0" role="region" aria-label="Classement des backs, défilement horizontal si nécessaire"><table>
        <caption>{PERIOD} · RB et FB · n = routes sous pression évaluables. Sélectionnez un joueur pour préparer une citation.</caption>
        <thead><tr><th scope="col">Rang ligue</th><th scope="col">Joueur / équipe(s) observée(s)</th><th scope="col">Taux régularisé</th><th scope="col">Taux brut</th><th scope="col">n évaluable</th><th scope="col">Percentile ligue</th></tr></thead>
        <tbody>{rows.map(row => <tr key={row.nflId} className={row.nflId === selected?.nflId ? 'bc-selected' : ''}>
          <td><span className="bc-rank">{row.rank.toString().padStart(2,'0')}</span></td><th scope="row"><button className="bc-player" aria-pressed={row.nflId === selected?.nflId} onClick={() => {setSelectedId(row.nflId); setCopyState('');}}>{row.displayName}<ArrowUpRight size={13} aria-hidden="true"/></button><small>{row.position} · {row.teams.join(' / ')}</small></th>
          <td><strong className="bc-rate">{formatRate(row.shrunkRate)}</strong><div className="bc-rate-track" aria-hidden="true"><span style={{width:`${row.shrunkRate * 100}%`}}/><i style={{left:`${reference.leagueAvailability * 100}%`}}/></div></td><td>{formatRate(row.rawRate)}</td><td>{formatNumber(row.counts.evaluatedPlays)}</td><td>{row.percentile == null ? 'Indisponible' : formatNumber(row.percentile)}</td>
        </tr>)}</tbody>
      </table></div>
      {!rows.length && <div className="bc-state" role="status"><h3>Aucun back éligible.</h3><p>Aucun joueur n’atteint le minimum publié de {reference.minN} routes pressurées évaluables.</p></div>}
      <p className="bc-table-note">Le repère vertical indique le taux brut ligue. La barre représente le taux régularisé : lissage vers cette référence, avec k = {reference.shrinkageK}. Les rangs et percentiles portent sur la cohorte ligue entière.</p>
    </section>
    {selected && <section className="bc-quote" aria-labelledby="bc-quote-title"><div className="bc-quote-label"><span className="bc-kicker">02 / PRÊT À CITER</span><h3 id="bc-quote-title">{selected.displayName}</h3><span>Chiffres publiés, phrase déterministe</span></div><div className="bc-quote-body"><blockquote>{quote}</blockquote><div className="bc-quote-footer"><span>Source : génération {season.manifest.generationId}</span><button onClick={copyQuote}>{copyState === 'copied' ? <Check size={14} aria-hidden="true"/> : <Copy size={14} aria-hidden="true"/>}{copyState === 'copied' ? 'Copié' : 'Copier la citation'}</button></div><p className="bc-copy-status" role="status">{copyState === 'failed' ? 'Copie automatique indisponible : sélectionnez le texte de la citation pour le copier.' : copyState === 'copied' ? 'Citation et source copiées.' : ''}</p></div></section>}
    <aside className="bc-limits" aria-labelledby="bc-limits-title"><span className="bc-kicker">LE CADRE DE LECTURE</span><h3 id="bc-limits-title">Une mesure de disponibilité, avec ses limites.</h3><p>Part des snaps sous pression où le RB était ouvert, à portée, assez avancé et orienté vers le QB. Reflète le joueur et le design de son attaque ; ce n’est pas une note causale.</p><p>Dénominateur : jeux pressurés où le RB court une route, avec verdict déterminé. Les observations inconnues sont exclues ; un jeu à deux backs peut compter pour chacun. L’orientation du corps est un proxy, pas une mesure du regard. La pression est détectée par proximité. Disponibilité ne signifie pas cible, complétion ou décision optimale.</p><p>Période limitée à {PERIOD}, pas une saison complète. Le taux régularisé sert au classement ; le taux brut reste distinct. Le percentile compare uniquement les backs éligibles. Aucun classement de talent ni effet causal ne peut être déduit de ces chiffres.</p></aside>
  </div>;
}
