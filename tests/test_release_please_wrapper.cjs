'use strict';
const assert = require('node:assert/strict');
const {test} = require('node:test');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const wrapper = require('../.github/actions/release-please/index.cjs');
const pkg = require('../.github/actions/release-please/package.json');
const env = {INPUT_TOKEN: 'synthetic-token', GITHUB_REPOSITORY: 'fixture/example',
  GITHUB_REF: 'refs/heads/main', GITHUB_EVENT_NAME: 'push'};
const config = {'.': {releaseType: 'simple', versionFile: 'version.txt',
  draft: true, forceTag: true, skipGithubRelease: false, includeComponentInTag: false}};
function fixture({releases = [], prs = [], repositoryConfig = config} = {}) {
  const calls = [];
  const manifest = {repositoryConfig,
    async createReleases() {calls.push('release'); return releases;},
    async createPullRequests() {calls.push('pr'); return prs;},
    async buildReleases() {calls.push('plan-release'); return [{}];},
    async buildPullRequests() {calls.push('plan-pr'); return [{}, {}];}};
  const api = {VERSION: pkg.dependencies['release-please'],
    GitHub: {async create(options) {calls.push(options); return {fixture: true};}},
    Manifest: {async fromManifest(...args) {calls.push(args); return manifest;}}};
  return {calls, api};
}
test('no release leaves upload outputs false and empty', async () => {
  const {api} = fixture({releases: [undefined], prs: [undefined]});
  assert.deepEqual(await wrapper.execute(env, api), {release_created: 'false',
    tag_name: '', sha: '', core_version: pkg.dependencies['release-please'], prs_created: 'false'});
});
test('root release exposes exact tag/SHA and reloads manifest before creating a PR', async () => {
  const {api, calls} = fixture({releases: [{path: '.', tagName: 'v0.2.0', sha: 'a'.repeat(40)}], prs: [{number: 123}]});
  const output = await wrapper.execute(env, api);
  assert.deepEqual([output.release_created, output.tag_name, output.sha, output.prs_created], ['true', 'v0.2.0', 'a'.repeat(40), 'true']);
  assert.equal(calls.filter(Array.isArray).length, 2);
  assert.deepEqual(calls.filter(x => typeof x === 'string'), ['release', 'pr']);
});
test('dry run outside main performs only planning', async () => {
  const {api, calls} = fixture();
  const result = await wrapper.execute({...env, GITHUB_REF: 'refs/heads/test',
    GITHUB_EVENT_NAME: 'pull_request', 'INPUT_DRY-RUN': 'true'}, api);
  assert.deepEqual(calls.filter(x => typeof x === 'string'), ['plan-release', 'plan-pr']);
  assert.deepEqual([result.release_created, result.planned_releases, result.planned_pull_requests], ['false', '1', '2']);
});
test('unsafe mutation contexts and malformed inputs fail before API access', async () => {
  for (const override of [{GITHUB_EVENT_NAME: 'pull_request'}, {GITHUB_REF: 'refs/heads/test'},
    {GITHUB_EVENT_NAME: 'pull_request_target'}, {GITHUB_EVENT_NAME: 'workflow_run'},
    {INPUT_TOKEN: ''}, {GITHUB_REPOSITORY: '../evil'}, {'INPUT_DRY-RUN': 'yes'}]) {
    const {api, calls} = fixture();
    await assert.rejects(wrapper.execute({...env, ...override}, api));
    assert.equal(calls.length, 0);
  }
});
test('installed core drift is rejected before network access', async () => {
  const {api, calls} = fixture(); api.VERSION = '0.0.0';
  await assert.rejects(wrapper.execute(env, api), /reviewed manifest/);
  assert.equal(calls.length, 0);
});
test('unsafe configs cannot create releases', async () => {
  for (const repositoryConfig of [{'.': {...config['.'], draft: false}},
    {'.': {...config['.'], forceTag: false}}, {'.': {...config['.'], skipGithubRelease: true}},
    {'.': {...config['.'], releaseType: 'node'}}, {'.': {...config['.'], versionFile: 'package.json'}},
    {'.': config['.'], other: config['.']}]) {
    const {api, calls} = fixture({repositoryConfig});
    await assert.rejects(wrapper.execute(env, api));
    assert.equal(calls.includes('release'), false);
  }
});

test('incompatible tag options fail before any release mutation', async () => {
  for (const override of [{includeComponentInTag: true}, {includeComponentInTag: undefined},
    {includeVInTag: false}, {includeVInTag: null}, {includeVInTag: 'true'}]) {
    const {api, calls} = fixture({repositoryConfig: {'.': {...config['.'], ...override}}});
    await assert.rejects(wrapper.execute(env, api), /v<SemVer>/);
    assert.equal(calls.includes('release'), false);
  }
  const {api} = fixture({repositoryConfig: {'.': {...config['.'], includeVInTag: true}}});
  assert.equal((await wrapper.execute(env, api)).release_created, 'false');
});
test('unexpected release outputs stop before another PR is planned', async () => {
  for (const release of [{path: 'other', tagName: 'v1.0.0', sha: 'a'.repeat(40)},
    {path: '.', tagName: 'v1.0.0\ninjected=true', sha: 'a'.repeat(40)},
    {path: '.', tagName: 'v1.0.0', sha: 'main'}]) {
    const {api, calls} = fixture({releases: [release]});
    await assert.rejects(wrapper.execute(env, api));
    assert.equal(calls.includes('pr'), false);
  }
});
test('GitHub output serialization rejects multiline injection', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'vlu-release-test-'));
  try {
    const file = path.join(dir, 'output');
    assert.throws(() => wrapper.writeOutputs(file, {sha: 'ok\ninjected=true'}));
    assert.equal(fs.existsSync(file), false);
    wrapper.writeOutputs(file, {release_created: 'false', sha: ''});
    assert.equal(fs.readFileSync(file, 'utf8'), 'release_created=false\nsha=\n');
  } finally {fs.rmSync(dir, {recursive: true});}
});
test('fetch rejects other origins before issuing a request', async () => {
  await assert.rejects(wrapper.boundedFetch('https://example.invalid/'), /Unexpected API/);
});
test('installed core exports the API contract used by the adapter', () => {
  assert.deepEqual(Object.keys(pkg.dependencies), ['release-please']);
  const api = require('../.github/actions/release-please/node_modules/release-please');
  assert.equal(api.VERSION, pkg.dependencies['release-please']);
  for (const method of ['createReleases', 'createPullRequests', 'buildReleases', 'buildPullRequests']) {
    assert.equal(typeof api.Manifest.prototype[method], 'function');
  }
  assert.equal(typeof api.Manifest.fromManifest, 'function');
  assert.equal(typeof api.GitHub.create, 'function');
});

test('owned runtime lock contains only registry packages with integrity', () => {
  const lock = require('../.github/actions/release-please/package-lock.json');
  assert.deepEqual(lock.packages[''].dependencies, pkg.dependencies);
  for (const [name, entry] of Object.entries(lock.packages)) {
    if (!name) continue;
    assert.ok(name.startsWith('node_modules/'), name);
    assert.ok(entry.resolved.startsWith('https://registry.npmjs.org/'), name);
    assert.match(entry.integrity, /^sha512-[A-Za-z0-9+/]+=*$/);
    assert.equal(entry.link, undefined);
  }
});
