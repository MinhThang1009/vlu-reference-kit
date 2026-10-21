// Exercise the parser resolved from the CLI, with bounded pathological inputs.
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { createRequire } = require('node:module');
const path = require('node:path');
const test = require('node:test');

const cliPackage = path.join(__dirname, '../node_modules/markdownlint-cli2/package.json');
const cliRequire = createRequire(cliPackage);
const MarkdownIt = cliRequire('markdown-it');
const childScript = `
  const { createRequire } = require('node:module');
  const MarkdownIt = createRequire(process.argv[1])('markdown-it');
  const scenario = process.argv[2];
  let rendered;
  if (scenario === 'reference') {
    rendered = new MarkdownIt().render('[a]: /u "' + 'x\\n'.repeat(200000));
  } else if (scenario === 'html') {
    const parser = new MarkdownIt({ html: true });
    for (const opener of ['<!--', '<?x', '<!A', '<![CDATA[']) {
      rendered = parser.render('x ' + opener.repeat(64000));
    }
  } else if (scenario === 'smartquotes') {
    rendered = new MarkdownIt({ typographer: true }).render('"a '.repeat(100000) + "b' ".repeat(100000));
  } else {
    throw new Error('Unknown synthetic scenario');
  }
  process.stdout.write(JSON.stringify({ renderedLength: rendered.length }));
`;

for (const scenario of ['reference', 'html', 'smartquotes']) {
  test(`CLI parser completes bounded ${scenario} input within five seconds`, () => {
    const result = spawnSync(process.execPath, ['-e', childScript, cliPackage, scenario], {
      cwd: path.join(__dirname, '..'),
      encoding: 'utf8',
      timeout: 5000,
      maxBuffer: 4096,
    });
    assert.equal(result.error, undefined, String(result.error));
    assert.equal(result.status, 0, result.stderr);
    assert.ok(JSON.parse(result.stdout).renderedLength > 0);
  });
}

test('CLI parser preserves Vietnamese text and ordinary Markdown rendering', () => {
  assert.equal(new MarkdownIt({ html: true }).render('VLU **Văn Lang**\n'),
    '<p>VLU <strong>Văn Lang</strong></p>\n');
});
