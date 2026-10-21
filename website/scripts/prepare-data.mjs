import {existsSync, readFileSync, mkdirSync, cpSync, rmSync, renameSync} from 'node:fs';
import {resolve, dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const source = resolve(root, process.env.RB_DATA_DIR || 'outputs/site');
const target = join(root, 'website/public/data');
const python = process.env.RB_PYTHON || [join(root,'.venv/bin/python'),join(root,'.venv/Scripts/python.exe')].find(existsSync);
function fail(message) { console.error(`RB Lifeline: ${message}`); process.exit(1); }
if (!existsSync(join(source,'manifest.json'))) fail(`Publication absent at ${source}. Run ./run --build-data first.`);
if (!python) fail('Python environment absent. Run ./prepare_environnement --no-skills first.');
console.log(`Validating real publication: ${source}`);
const result = spawnSync(python, ['-m','rb_lifeline','validate','--output',source,'--check-source',...(process.env.RB_SOURCE_DIR ? ['--data-dir',process.env.RB_SOURCE_DIR] : [])], {cwd:root,stdio:'inherit'});
if (result.error || result.status !== 0) fail('Publication validation failed; regenerate with ./run --build-data.');
const manifest = JSON.parse(readFileSync(join(source,'manifest.json'),'utf8'));
const staging = `${target}.staging`;
rmSync(staging,{recursive:true,force:true});
mkdirSync(join(staging,'generations'),{recursive:true});
// Copy only the manifest-selected generation; historical generations remain local.
cpSync(join(source,'generations',manifest.generationId),join(staging,'generations',manifest.generationId),{recursive:true});
cpSync(join(source,'manifest.json'),join(staging,'manifest.json'));
rmSync(target,{recursive:true,force:true});
renameSync(staging,target);
console.log(`Prepared generation ${manifest.generationId}: ${manifest.counts.gameCount} games, ${manifest.counts.playCount} dropbacks with observed trajectories.`);
