export const FIELD_WIDTH = 120;
export const FIELD_HEIGHT = 53.3;

export const STATUS_LABELS = {
  available: '✓ Disponible',
  unavailable: '✗ Indisponible',
  blocking: '▰ Au bloc',
  unknown: '? Indéterminé',
};

export function orientationVector(degrees, length = 2.4) {
  const radians = degrees * Math.PI / 180;
  return { x: Math.sin(radians) * length, y: -Math.cos(radians) * length };
}

// A missing frame or participant breaks a trail; never bridge an observation gap.
export function trailSegments(frames, index, nflId, full = false) {
  const segments = [];
  let segment = [];
  const start = full ? 0 : Math.max(0, index - 7);
  for (let i = start; i <= index; i += 1) {
    const frame = frames[i];
    const entity = frame.entities.find((point) => point.nflId === nflId);
    const gap = i > start && frame.frameId !== frames[i - 1].frameId + 1;
    if (!entity || gap) {
      if (segment.length > 1) segments.push(segment);
      segment = [];
    }
    if (entity) segment.push([entity.x, FIELD_HEIGHT - entity.y]);
  }
  if (segment.length > 1) segments.push(segment);
  return segments;
}

export function nextPlaybackIndex(frames, currentIndex, timeS, pressureIndex, pressureVisited) {
  let next = currentIndex;
  while (next + 1 < frames.length && frames[next + 1].timeS <= timeS + 1e-8) next += 1;
  if (!pressureVisited && pressureIndex > currentIndex && next >= pressureIndex) {
    return { index: pressureIndex, stop: true, pressureVisited: true };
  }
  return { index: next, stop: next === frames.length - 1, pressureVisited };
}
