'use strict';

const fs = require('node:fs');

function inputs(env) {
  const token = env.INPUT_TOKEN;
  if (typeof token !== 'string' || !token.trim()) throw new Error('A token is required.');
  const repository = env.GITHUB_REPOSITORY || '';
  if (!/^[A-Za-z0-9][A-Za-z0-9-]{0,38}\/[A-Za-z0-9_.-]+$/.test(repository) ||
      ['.', '..'].includes(repository.split('/')[1])) {
    throw new Error('GITHUB_REPOSITORY must identify one owner/repository.');
  }
  const dryRun = env['INPUT_DRY-RUN'] || 'false';
  if (!['true', 'false'].includes(dryRun)) throw new Error('dry-run must be true or false.');
  if (dryRun === 'false' && (env.GITHUB_REF !== 'refs/heads/main' ||
      !['push', 'workflow_dispatch'].includes(env.GITHUB_EVENT_NAME))) {
    throw new Error('Release mutations are restricted to trusted main push/dispatch runs.');
  }
  return {token, repository, dryRun: dryRun === 'true'};
}

function validateManifest(manifest) {
  if (Object.keys(manifest.repositoryConfig).join(',') !== '.') {
    throw new Error('Only the root kit package may be released.');
  }
  const config = manifest.repositoryConfig['.'];
  if (config.releaseType !== 'simple' || config.versionFile !== 'version.txt' ||
      config.draft !== true || config.forceTag !== true || config.skipGithubRelease !== false) {
    throw new Error('Release config must retain the simple/version.txt draft-and-tag policy.');
  }
  if (config.includeComponentInTag !== false ||
      (config.includeVInTag !== undefined && config.includeVInTag !== true)) {
    throw new Error('Release tags must use v<SemVer> without a component prefix.');
  }
}

async function boundedFetch(url, options = {}) {
  const target = new URL(typeof url === 'string' ? url : url.url);
  if (target.origin !== 'https://api.github.com') throw new Error('Unexpected API destination.');
  return fetch(url, {...options, signal: AbortSignal.timeout(30000), redirect: 'error'});
}

async function execute(env, api) {
  const input = inputs(env);
  const expected = require('./package.json').dependencies['release-please'];
  if (api.VERSION !== expected) throw new Error('Installed core differs from the reviewed manifest.');
  const [owner, repo] = input.repository.split('/');
  const github = await api.GitHub.create({owner, repo, token: input.token,
    defaultBranch: 'main', apiUrl: 'https://api.github.com',
    graphqlUrl: 'https://api.github.com', fetch: boundedFetch});
  const load = async () => {
    const manifest = await api.Manifest.fromManifest(github, 'main',
      'release-please-config.json', '.release-please-manifest.json');
    validateManifest(manifest);
    return manifest;
  };
  const manifest = await load();
  const output = {release_created: 'false', tag_name: '', sha: '',
    core_version: api.VERSION, prs_created: 'false'};
  if (input.dryRun) {
    output.planned_releases = String((await manifest.buildReleases()).length);
    output.planned_pull_requests = String((await manifest.buildPullRequests()).length);
    return output;
  }
  const releases = (await manifest.createReleases()).filter(release => release !== undefined);
  if (releases.length > 1 || releases.some(release => release.path !== '.')) {
    throw new Error('Core returned an unexpected release package.');
  }
  if (releases.length) {
    const release = releases[0];
    if (!/^v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$/.test(release.tagName) ||
        !/^[0-9a-f]{40}$/.test(release.sha)) {
      throw new Error('Core returned an invalid release tag or commit SHA.');
    }
    Object.assign(output, {release_created: 'true', tag_name: release.tagName, sha: release.sha});
  }
  // Reload after creating a release so PR planning uses the new release state.
  const prs = (await (await load()).createPullRequests()).filter(pr => pr !== undefined);
  output.prs_created = String(prs.length > 0);
  return output;
}

function writeOutputs(file, values) {
  const lines = Object.entries(values).map(([key, value]) => {
    if (!/^[a-z_]+$/.test(key) || typeof value !== 'string' || /[\r\n]/.test(value)) {
      throw new Error('Invalid GitHub output.');
    }
    return `${key}=${value}\n`;
  });
  fs.appendFileSync(file, lines.join(''), 'utf8');
}

function commandText(value) {
  return value.replaceAll('%', '%25').replaceAll('\r', '%0D').replaceAll('\n', '%0A');
}

async function main(env = process.env) {
  const input = inputs(env);
  console.log(`::add-mask::${commandText(input.token)}`);
  try {
    const api = require('release-please');
    const output = await execute(env, api);
    if (!env.GITHUB_OUTPUT) throw new Error('GITHUB_OUTPUT is required.');
    writeOutputs(env.GITHUB_OUTPUT, output);
    console.log(`Release Please core ${output.core_version}; dry-run=${input.dryRun}`);
  } catch (error) {
    const message = String(error.message).replaceAll(input.token, '[REDACTED]');
    throw new Error(message);
  }
}

module.exports = {inputs, validateManifest, boundedFetch, execute, writeOutputs, main};
if (require.main === module) {
  main().catch(error => {
    console.error(`::error::${commandText(error.message)}`);
    process.exitCode = 1;
  });
}
