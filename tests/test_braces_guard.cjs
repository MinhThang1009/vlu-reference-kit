// Kiểm tra parser thực tế sau npm ci và bản vá cục bộ của repo.
const assert = require('node:assert/strict');
const test = require('node:test');
const braces = require('braces');
const micromatch = require('micromatch');
const pattern = (depth) => '{'.repeat(depth) + 'x' + '}'.repeat(depth);
const rejectsDepth = (error) => error instanceof SyntaxError && error.message.includes('VLU_BRACES_MAX_DEPTH');

for (const name of ['parse', 'compile', 'expand', 'stringify', 'create']) {
  test(`${name} rejects deep string input before recursive walking`, () => {
    assert.throws(() => braces[name](pattern(4000)), rejectsDepth);
  });
}

test('default and array entry points use the guarded parser', () => {
  assert.throws(() => braces(pattern(4000)), rejectsDepth);
  assert.throws(() => braces(['normal', pattern(4000)]), rejectsDepth);
});

test('parentheses and mixed AST nesting cannot bypass the limit', () => {
  assert.throws(() => braces.compile('('.repeat(101) + 'x' + ')'.repeat(101)), rejectsDepth);
  assert.throws(() => braces.compile('{('.repeat(51) + 'x' + ')}'.repeat(51)), rejectsDepth);
});

test('boundary accepts 100 levels and refuses 101, even with caller options', () => {
  assert.doesNotThrow(() => braces.compile(pattern(100)));
  assert.throws(() => braces.compile(pattern(101), { maxDepth: Infinity }), rejectsDepth);
});

test('normal alternatives, ranges and escaped or quoted braces remain supported', () => {
  assert.deepEqual(braces.expand('file-{a,b}-{1..2}.md'), ['file-a-1.md', 'file-a-2.md', 'file-b-1.md', 'file-b-2.md']);
  assert.equal(braces.compile('"' + '{'.repeat(200) + '"'), '{'.repeat(200));
  assert.equal(braces.compile('\\{'.repeat(200)), '{'.repeat(200));
});

test('micromatch brace APIs resolve the guarded dependency', () => {
  assert.deepEqual(micromatch(['a.md', 'b.txt', 'c.js'], '*.{md,txt}'), ['a.md', 'b.txt']);
  assert.throws(() => micromatch.braces(pattern(4000)), rejectsDepth);
  assert.throws(() => micromatch.braceExpand(pattern(4000)), rejectsDepth);
});

test('reapplying the reviewed patch preserves installed bytes', () => {
  const fs = require('node:fs');
  const path = require('node:path');
  const { execFileSync } = require('node:child_process');
  const sourcePath = require.resolve('braces/lib/parse');
  const before = fs.readFileSync(sourcePath);
  execFileSync('python', [path.join(__dirname, '../scripts/patch_braces.py')], { timeout: 15000 });
  assert.deepEqual(fs.readFileSync(sourcePath), before);
});
