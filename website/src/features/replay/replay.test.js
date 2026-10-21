import test from 'node:test';
import assert from 'node:assert/strict';
import { nextPlaybackIndex, orientationVector, trailSegments } from './replay.js';

test('playback stops exactly at pressure after delayed clock and continues explicitly', () => {
  const frames = [0, .1, .2, .3, .4].map((timeS, index) => ({ timeS, frameId: 20 + index }));
  assert.deepEqual(nextPlaybackIndex(frames, 0, .35, 2, false), { index: 2, stop: true, pressureVisited: true });
  assert.deepEqual(nextPlaybackIndex(frames, 2, .35, 2, true), { index: 3, stop: false, pressureVisited: true });
  assert.deepEqual(nextPlaybackIndex(frames, 2, 10, 2, true), { index: 4, stop: true, pressureVisited: true });
});

test('playback without pressure reaches last observed frame without extrapolation', () => {
  const frames = [{ timeS: 0 }, { timeS: .1 }];
  assert.deepEqual(nextPlaybackIndex(frames, 0, 100, -1, false), { index: 1, stop: true, pressureVisited: false });
});

test('body orientation projects source compass angles onto inverted SVG y', () => {
  assert.deepEqual(orientationVector(0, 1), { x: 0, y: -1 });
  assert.ok(Math.abs(orientationVector(90, 1).x - 1) < 1e-8);
  assert.ok(Math.abs(orientationVector(180, 1).y - 1) < 1e-8);
  assert.ok(Math.abs(orientationVector(270, 1).x + 1) < 1e-8);
});

test('trails use past observations only and break on participant and source frame gaps', () => {
  const frame = (frameId, present = true) => ({ frameId, entities: present ? [{ nflId: 'rb', x: frameId, y: 10 }] : [] });
  const frames = [frame(1), frame(2), frame(3, false), frame(4), frame(5), frame(8), frame(9), frame(10)];
  const segments = trailSegments(frames, 6, 'rb', true);
  assert.deepEqual(segments.map((segment) => segment.map(([x]) => x)), [[1, 2], [4, 5], [8, 9]]);
  assert.equal(trailSegments(frames, 0, 'rb', true).length, 0);
});
