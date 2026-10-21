import React, { useEffect, useRef, useState } from 'react';
import PressurePanel from './PressurePanel.jsx';
import { FIELD_HEIGHT, STATUS_LABELS, orientationVector, trailSegments, nextPlaybackIndex } from './replay.js';
import './replay.css';

/** @param {{play: object, players: object, selectedNflId: string|null, onSelectBack: Function, parameters?: object, onFrameChange?: Function}} props */
export default function FieldAnimation(props) {
  return <Replay {...props} />;
}

function Replay({ play, players = {}, selectedNflId, onSelectBack, parameters = {}, onFrameChange }) {
  const frames = play?.frames ?? [];
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const pressureVisited = useRef(false);
  const frame = frames[index];
  const pressureIndex = frames.findIndex((item) => item.frameId === play?.events?.pressureFrameId);
  const qbId = play?.participants?.find((item) => item.role === 'passer')?.nflId;
  const backs = play?.observations ?? [];
  const backId = backs.some((item) => item.nflId === selectedNflId) ? selectedNflId : backs[0]?.nflId;
  const observation = backs.find((item) => item.nflId === backId);
  const currentState = frame?.rbStates?.find((item) => item.nflId === backId);
  const status = currentState?.status ?? 'unknown';

  useEffect(() => {
    setIndex(0);
    // Start the replay on open unless the viewer asked for reduced motion.
    setPlaying(!globalThis.matchMedia?.('(prefers-reduced-motion: reduce)').matches);
    pressureVisited.current = false;
  }, [play]);
  useEffect(() => { onFrameChange?.(frame); }, [frame, onFrameChange]);
  useEffect(() => {
    if (!playing || !frame) return undefined;
    const start = performance.now();
    const startTime = frame.timeS;
    let timer;
    const tick = () => {
      const result = nextPlaybackIndex(frames, index, startTime + (performance.now() - start) / 1000 * speed, pressureIndex, pressureVisited.current);
      pressureVisited.current = result.pressureVisited;
      setIndex(result.index);
      if (result.stop) setPlaying(false);
      else timer = requestAnimationFrame(tick);
    };
    timer = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(timer);
    // Keep a continuous wall clock throughout a playback run, not one per rendered frame.
  }, [playing, speed, frames, pressureIndex]);

  const seek = (next) => {
    setPlaying(false);
    setIndex(next);
    pressureVisited.current = pressureIndex >= 0 && next >= pressureIndex;
  };
  const restart = () => { seek(0); pressureVisited.current = false; };
  const togglePlay = () => {
    if (index === frames.length - 1) { setIndex(0); pressureVisited.current = false; }
    if (index === pressureIndex) pressureVisited.current = true;
    setPlaying(!playing);
  };

  if (!play) return <p className="replay-empty">Select a play to replay its frames.</p>;
  if (!frame) return <section className="replay-empty"><h3>Replay unavailable</h3><p>No observed frame for this play.</p><p>{play.quality?.reasons?.join(' · ')}</p></section>;

  return <div className="replay-component">
    <div className="replay-panel-heading"><h3>Dropback replay</h3><span>Offense → · normalized coordinates · yards</span></div>
    <div className="replay-back-picker"><label>Tracked back <select value={backId ?? ''} onChange={(event) => onSelectBack?.(event.target.value)} disabled={!backs.length}>{!backs.length && <option value="">No back observed</option>}{backs.map((back) => <option key={back.nflId} value={back.nflId}>{players[back.nflId]?.displayName ?? back.nflId} · {players[back.nflId]?.officialPosition ?? 'Back'}</option>)}</select></label><strong className={`replay-status replay-status-${status}`}>{STATUS_LABELS[status]}</strong></div>
    <PlayOutcome play={play} observation={observation} players={players} />
    <svg className="replay-field" viewBox="-2 -3 124 60" role="img" aria-label={`Field at ${frame.timeS.toFixed(1)} seconds, frame ${frame.frameId}. ${STATUS_LABELS[status]}`}>
      <title>Observed positions of players and ball</title>
      <desc>A 120 by 53.3 yard field. The offense moves right. Arrows show body orientation. Text measurements are listed below the field.</desc>
      <rect x="0" y="0" width="120" height={FIELD_HEIGHT} fill="#123d32" stroke="#b6c6b8" strokeWidth=".2" />
      <rect x="0" y="0" width="10" height={FIELD_HEIGHT} fill="#14302d" /><rect x="110" y="0" width="10" height={FIELD_HEIGHT} fill="#14302d" />
      {Array.from({ length: 11 }, (_, i) => i * 10 + 10).map((x) => <g key={x}><line x1={x} y1="0" x2={x} y2={FIELD_HEIGHT} stroke="#d3e9de" strokeOpacity=".48" strokeWidth=".18" />{x > 10 && x < 110 && <><text x={x} y="5" textAnchor="middle" fill="#cfdbd4" fontSize="2">{50 - Math.abs(60 - x)}</text><text x={x} y="50" textAnchor="middle" fill="#cfdbd4" fontSize="2">{50 - Math.abs(60 - x)}</text></>}</g>)}
      {typeof play.losX === 'number' && <g><line x1={play.losX} y1="0" x2={play.losX} y2={FIELD_HEIGHT} stroke="#ecc44d" strokeWidth=".35" strokeDasharray="1 .8" /><text x={play.losX + 1} y="-1" fill="currentColor" fontSize="1.7">Line at snap</text></g>}
      {frame.entities.filter((entity) => entity.nflId !== null).map((entity) => {
        const primary = entity.nflId === backId || entity.nflId === qbId;
        return trailSegments(frames, index, entity.nflId, primary).map((segment, segmentIndex) => <polyline key={`${entity.nflId}-${segmentIndex}`} points={segment.map((point) => point.join(',')).join(' ')} fill="none" stroke={entity.nflId === backId ? '#f4dc90' : entity.nflId === qbId ? '#78d9f1' : '#e8eee8'} strokeWidth={primary ? '.35' : '.18'} opacity={primary ? '.85' : '.2'} />);
      })}
      {frame.entities.map((entity) => {
        const ball = entity.nflId === null || entity.team === 'football';
        const back = entity.nflId === backId;
        const qb = entity.nflId === qbId;
        const defender = entity.nflId === play.pressure?.defenderId && index === pressureIndex;
        const color = back ? ({ available: '#55db9c', unavailable: '#fa8484', blocking: '#a9b4bb', unknown: '#e0c879' }[status]) : qb ? '#7ddaf5' : entity.team === play.possessionTeam ? '#dbe9f0' : '#eea178';
        const vector = typeof entity.o === 'number' && (qb || back) ? orientationVector(entity.o) : null;
        return <g key={entity.nflId ?? 'football'} transform={`translate(${entity.x} ${FIELD_HEIGHT - entity.y})`}><title>{ball ? 'Ball' : `${players[entity.nflId]?.displayName ?? entity.nflId} · ${entity.team}${back ? ` · ${STATUS_LABELS[status]}` : ''}`} · x {entity.x}, y {entity.y}</title>
          {defender && <circle r="2.2" fill="none" stroke="#ffe16a" strokeWidth=".4" strokeDasharray=".4 .3" />}
          {ball ? <ellipse rx=".7" ry=".45" fill="#edbc7a" stroke="#24180c" strokeWidth=".2" /> : <><circle r={qb || back ? '1.25' : '.95'} fill={color} stroke="#0a171b" strokeWidth=".23" />{vector && <g stroke={color} strokeWidth=".35"><line x1="0" y1="0" x2={vector.x} y2={vector.y} /><path d={`M ${vector.x * .72 - vector.y * .2} ${vector.y * .72 + vector.x * .2} L ${vector.x} ${vector.y} L ${vector.x * .72 + vector.y * .2} ${vector.y * .72 - vector.x * .2}`} fill="none" /></g>}<text y=".5" textAnchor="middle" fill="#07151b" fontSize={back ? '1.6' : '1.1'} fontWeight="700">{back ? ({ available: '✓', unavailable: '✗', blocking: 'B', unknown: '?' }[status]) : qb ? 'QB' : ''}</text></>}
        </g>;
      })}
    </svg>
    <p className="replay-legend">● Blue: QB · light: offense · orange: defense · oval: ball · arrows: body orientation · yellow circle: defender who triggered the pressure. Trails: past observed positions.</p>
    <div className="replay-controls" role="group" aria-label="Playback controls">
      <button type="button" onClick={restart}>↺ Start</button><button type="button" onClick={() => seek(Math.max(0, index - 1))} disabled={index === 0}>← Frame</button><button type="button" onClick={togglePlay} aria-pressed={playing}>{playing ? 'Ⅱ Pause' : '▶ Play'}</button><button type="button" onClick={() => seek(Math.min(frames.length - 1, index + 1))} disabled={index === frames.length - 1}>Frame →</button>
      <label>Speed <select value={speed} onChange={(event) => { setPlaying(false); setSpeed(Number(event.target.value)); }}><option value="0.5">0.5×</option><option value="1">1×</option></select></label>
      <button type="button" disabled={pressureIndex < 0} onClick={() => seek(pressureIndex)}>At pressure{play.pressure?.timeS != null ? ` (${play.pressure.timeS.toFixed(1)} s)` : ''}</button>
    </div>
    <label className="replay-scrubber">Time: {frame.timeS.toFixed(1)} s · frame {frame.frameId}<span className="replay-timeline"><input type="range" min="0" max={frames.length - 1} step="1" value={index} onChange={(event) => seek(Number(event.target.value))} aria-label="Replay frame" aria-valuetext={`${frame.timeS.toFixed(1)} seconds, frame ${frame.frameId}`} />{pressureIndex >= 0 && <span className="replay-pressure-marker" style={{ left: `${frames.length > 1 ? pressureIndex / (frames.length - 1) * 100 : 0}%` }} title={`Pressure at frame ${play.events.pressureFrameId}`} aria-hidden="true">▴</span>}</span></label>
    <p className="replay-note">{pressureIndex >= 0 ? 'Auto-pause at the first pressure. Press Play to continue.' : play.pressure?.status === 'none' ? 'No pressure detected → not counted. The replay remains available.' : 'Pressure moment undetermined.'} Observed end: {play.events?.endKind ?? 'unknown'}. {play.quality?.reasons?.join(' · ')}</p>
    <PressurePanel observation={observation} parameters={parameters} pressure={play.pressure} />
    <details className="replay-text"><summary>Text alternative: positions at this frame</summary><table className="replay-checks"><thead><tr><th>Participant</th><th>Team</th><th>x (yd)</th><th>y (yd)</th><th>Orientation</th></tr></thead><tbody>{frame.entities.map((entity) => <tr key={entity.nflId ?? 'football'}><th scope="row">{entity.nflId === null ? 'Ball' : players[entity.nflId]?.displayName ?? entity.nflId}</th><td>{entity.team}</td><td>{entity.x}</td><td>{entity.y}</td><td>{entity.o == null ? 'Undetermined' : `${entity.o}°`}</td></tr>)}</tbody></table></details>
  </div>;
}

/** What happened on the play and what the followed back did in it, read from published fields only. */
function PlayOutcome({ play, observation, players }) {
  const result = PASS_RESULTS[play.passResult];
  const yards = typeof play.playResult === 'number' ? `${play.playResult > 0 ? '+' : ''}${play.playResult} yd` : null;
  const name = (id) => players[id]?.displayName ?? id;
  const targetName = play.target?.status === 'matched' && play.target.nflId !== observation?.nflId ? name(play.target.nflId) : null;
  let targeted = ['unknown', 'Unknown'];
  let caught = ['unknown', 'Unknown'];
  if (!observation) targeted = caught = ['unknown', 'No RB observed'];
  else if (observation.targetStatus === 'not_applicable') targeted = caught = ['neutral', 'No pass'];
  else if (observation.targetStatus === 'matched') {
    targeted = observation.targeted ? ['yes', 'Yes'] : ['no', 'No'];
    caught = !observation.targeted ? ['neutral', 'Not targeted'] : observation.completedWhenTargeted === true ? ['yes', 'Yes'] : observation.completedWhenTargeted === false ? ['no', 'No'] : ['unknown', 'Unknown'];
  }
  const available = play.pressure?.status === 'none' ? ['neutral', 'No pressure'] : { available: ['yes', 'Yes'], unavailable: ['no', 'No'], blocking: ['neutral', 'Blocking'] }[observation?.status] ?? ['unknown', 'Undetermined'];
  return <dl className="play-outcome" aria-label="Play outcome and RB role">
    <div className={`play-outcome-item outcome-${result?.tone ?? 'unknown'}`}><dt>Play outcome</dt><dd>{result?.label ?? 'Unavailable'}{yards && <small>{yards}</small>}</dd></div>
    <div className={`play-outcome-item outcome-${targeted[0]}`}><dt>RB targeted</dt><dd>{targeted[1]}{targetName && <small>Pass to {targetName}</small>}</dd></div>
    <div className={`play-outcome-item outcome-${caught[0]}`}><dt>RB caught it</dt><dd>{caught[1]}</dd></div>
    <div className={`play-outcome-item outcome-${available[0]}`}><dt>RB open at pressure</dt><dd>{available[1]}</dd></div>
  </dl>;
}
const PASS_RESULTS = {
  C: { label: 'Complete pass', tone: 'yes' },
  I: { label: 'Incomplete pass', tone: 'no' },
  IN: { label: 'Interception', tone: 'no' },
  S: { label: 'Sack', tone: 'no' },
  R: { label: 'QB scramble', tone: 'neutral' },
};
