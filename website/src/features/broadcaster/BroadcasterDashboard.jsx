import React, {useRef, useState} from 'react';
import {ArrowUpRight, Check, Copy, Mic2} from 'lucide-react';
import {PERIOD, formatNumber, formatRate, leagueRows, quoteFor} from './broadcaster.js';
import './broadcaster.css';

export default function BroadcasterDashboard({season}) {
  const [selectedId, setSelectedId] = useState(null);
  const [copyState, setCopyState] = useState('');
  const quoteRef = useRef(null);
  const rows = leagueRows(season?.rb);
  const reference = season?.rb?.reference;
  if (!rows || !Number.isFinite(reference.leagueAvailability)) return <section className="bc-state" role="alert"><h2>Ranking unavailable.</h2><p>The published season table cannot support a verified ranking.</p></section>;
  const selected = rows.find(row => row.nflId === selectedId) || rows[0];
  const quote = selected ? quoteFor(selected) : '';
  async function copyQuote() {
    try {
      await navigator.clipboard.writeText(`${quote}\nSource: generation ${season.manifest.generationId}.`);
      setCopyState('copied');
    } catch { setCopyState('failed'); }
  }
  // The quote sits above the ranking, so bring it back into view when a player is picked below.
  function selectPlayer(nflId) {
    setSelectedId(nflId); setCopyState('');
    quoteRef.current?.scrollIntoView({block: 'nearest', behavior: 'smooth'});
  }
  return <div className="broadcaster">
    <section className="bc-overview" aria-labelledby="bc-title">
      <div><span className="bc-kicker"><Mic2 size={14} aria-hidden="true"/> ON-AIR NOTE / {PERIOD}</span><h2 id="bc-title">Best safety valves<span>The outlets, by the numbers.</span></h2><p>The league ranking of eligible RBs and FBs. A descriptive read to prepare your next segment, with every number tied to the same publication.</p></div>
      <div className="bc-reference"><span>LEAGUE REFERENCE · PLAYER-PLAY</span><strong>{formatRate(reference.leagueAvailability)}</strong><p>Published raw availability rate</p><div><span>{reference.cohortSize} eligible backs</span><span>Minimum n = {reference.minN}</span></div></div>
    </section>
    {selected && <section className="bc-quote" aria-labelledby="bc-quote-title" ref={quoteRef}><div className="bc-quote-label"><span className="bc-kicker">01 / READY TO QUOTE</span><h3 id="bc-quote-title">{selected.displayName}</h3><span>Published figures, deterministic sentence. Pick another player in the ranking below.</span></div><div className="bc-quote-body"><blockquote>{quote}</blockquote><div className="bc-quote-footer"><span>Source: generation {season.manifest.generationId}</span><button onClick={copyQuote}>{copyState === 'copied' ? <Check size={14} aria-hidden="true"/> : <Copy size={14} aria-hidden="true"/>}{copyState === 'copied' ? 'Copied' : 'Copy quote'}</button></div><p className="bc-copy-status" role="status">{copyState === 'failed' ? 'Automatic copy unavailable: select the quote text to copy it.' : copyState === 'copied' ? 'Quote and source copied.' : ''}</p></div></section>}
    <section className="bc-ranking" aria-labelledby="bc-ranking-title">
      <div className="bc-table-heading"><div><span className="bc-kicker">02 / LEAGUE RANKING</span><h3 id="bc-ranking-title">Who offers an outlet under pressure?</h3></div><span className="bc-order">Published order · regularized rate, descending</span></div>
      <div className="bc-table-scroll" tabIndex="0" role="region" aria-label="Back ranking, scrolls horizontally if needed"><table>
        <caption>{PERIOD} · RBs and FBs · n = evaluable routes under pressure. Select a player to prepare a quote.</caption>
        <thead><tr><th scope="col">League rank</th><th scope="col">Player / observed team(s)</th><th scope="col">Regularized rate</th><th scope="col">Raw rate</th><th scope="col">Evaluable n</th><th scope="col">League percentile</th></tr></thead>
        <tbody>{rows.map(row => <tr key={row.nflId} className={row.nflId === selected?.nflId ? 'bc-selected' : ''}>
          <td><span className="bc-rank">{row.rank.toString().padStart(2,'0')}</span></td><th scope="row"><button className="bc-player" aria-pressed={row.nflId === selected?.nflId} onClick={() => selectPlayer(row.nflId)}>{row.displayName}<ArrowUpRight size={13} aria-hidden="true"/></button><small>{row.position} · {row.teams.join(' / ')}</small></th>
          <td><strong className="bc-rate">{formatRate(row.shrunkRate)}</strong><div className="bc-rate-track" aria-hidden="true"><span style={{width:`${row.shrunkRate * 100}%`}}/><i style={{left:`${reference.leagueAvailability * 100}%`}}/></div></td><td>{formatRate(row.rawRate)}</td><td>{formatNumber(row.counts.evaluatedPlays)}</td><td>{row.percentile == null ? 'Unavailable' : formatNumber(row.percentile)}</td>
        </tr>)}</tbody>
      </table></div>
      {!rows.length && <div className="bc-state" role="status"><h3>No eligible back.</h3><p>No player reaches the published minimum of {reference.minN} evaluable pressured routes.</p></div>}
      <p className="bc-table-note">The vertical marker shows the league raw rate. The bar shows the regularized rate: shrinkage towards that reference, with k = {reference.shrinkageK}. Ranks and percentiles cover the whole league cohort.</p>
    </section>
    <aside className="bc-limits" aria-labelledby="bc-limits-title"><span className="bc-kicker">HOW TO READ IT</span><h3 id="bc-limits-title">An availability measure, with its limits.</h3><p>Share of pressured snaps where the RB was open, in range, far enough downfield and facing the QB. It reflects both the player and the offensive design; it is not a causal grade.</p><p>Denominator: pressured plays where the RB runs a route, with a determined verdict. Unknown observations are excluded; a play with two backs can count for each. Body orientation is a proxy, not a measure of gaze. Pressure is detected by proximity. Availability does not mean target, completion or optimal decision.</p><p>Period limited to {PERIOD}, not a full season. The regularized rate drives the ranking; the raw rate stays separate. The percentile only compares eligible backs. No talent ranking or causal effect can be inferred from these figures.</p></aside>
  </div>;
}
