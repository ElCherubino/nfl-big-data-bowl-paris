import test from 'node:test';
import assert from 'node:assert/strict';
import {createSiteData} from '../src/data/siteData.js';

function fixture(overrides = {}) {
  const envelope = data => ({schemaVersion: '1.0.0', generationId: 'test', data});
  const docs = {
    'manifest.json': {schemaVersion: '1.0.0', generationId: 'test', parameters: {}, period: {}, counts: {}, resources: {games: 'games.json', seasonRb: 'rb.json', seasonTeam: 'teams.json', analysis: 'analysis.json', quality: 'quality.json'}},
    'games.json': envelope([{gameId: '1', gameResource: 'game_1.json'}]),
    'game_1.json': envelope({gameId: '1', players: {}, plays: [], rbSummary: []}),
    ...overrides,
  };
  const calls = [];
  return {calls, client: createSiteData({manifestUrl: 'http://localhost/prefix/data/manifest.json', fetcher: async url => {
    calls.push(String(url)); const doc = docs[String(url).split('/').at(-1)];
    return {ok: !!doc, status: doc ? 200 : 404, json: async () => structuredClone(doc)};
  }})};
}
test('loads resources relative to manifest under deployment prefix and caches validated game', async () => {
  const {client, calls} = fixture();
  assert.equal((await client.loadCatalog()).games[0].gameId, '1');
  await client.loadGame('1'); await client.loadGame('1');
  assert.equal(calls.length, 3); assert.ok(calls.every(url => url.includes('/prefix/data/')));
});
test('rejects mixed generations and unlisted games', async () => {
  const {client} = fixture({'game_1.json': {schemaVersion: '1.0.0', generationId: 'stale', data: {}}});
  await assert.rejects(client.loadGame('1'), e => e.code === 'GENERATION_MISMATCH');
  await assert.rejects(client.loadGame('2'), e => e.code === 'INVALID_DOCUMENT');
});
test('rejects paths outside publication and incompatible schema', async () => {
  const {client} = fixture({'games.json': {schemaVersion: '1.0.0', generationId: 'test', data: [{gameId: '1', gameResource: '../secret.json'}]}});
  await assert.rejects(client.loadCatalog(), e => e.code === 'INVALID_DOCUMENT');
  const bad = fixture({'manifest.json': {schemaVersion: '2.0.0'}});
  await assert.rejects(bad.client.loadCatalog(), e => e.code === 'UNSUPPORTED_SCHEMA');
});
