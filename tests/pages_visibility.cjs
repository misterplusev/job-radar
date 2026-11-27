/* Hosted fixture test: node --test test_pages_visibility.cjs */
const test = require("node:test");
const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { join } = require("node:path");
const vm = require("node:vm");
const workflow = readFileSync(join(__dirname, "..", ".github", "workflows", "sports-teams.yml"), "utf8")
  .replace(/\r\n/g,"\n");
const afterName = workflow.split("      - name: Wait for the board artifact to be visible to Pages\n")[1];
const block = afterName.split("      - uses: actions/deploy-pages@v4")[0];
const source = block.split("          script: |\n")[1].trimEnd().split("\n").map(l => l.slice(12)).join("\n");
const match = {name: "github-pages", size: 17};

async function fixture(replies) {
  let requests = 0;
  const run = vm.runInNewContext("(async () => {" + source + "})", {
    process: {env: {ACTIONS_RESULTS_URL:"https://fixture.invalid",
      ACTIONS_RUNTIME_TOKEN:"fixture."+Buffer.from('{"scp":"Actions.Results:r:j"}').toString("base64url")+".fixture"}},
    Buffer, URL, AbortSignal,
    setTimeout(fn) { fn(); },
    fetch: async (url, init) => {
      assert.equal(url.pathname, "/twirp/github.actions.results.api.v1.ArtifactService/ListArtifacts");
      assert.deepEqual(JSON.parse(init.body), {workflowRunBackendId:"r",workflowJobRunBackendId:"j"});
      const reply = replies[Math.min(requests++,replies.length-1)];
      return {ok: Array.isArray(reply), status: Array.isArray(reply) ? 200 : reply,
              json: async () => ({artifacts:reply})};
    }
  });
  await run();
  return requests;
}
test("wait for this run's nonempty Pages artifact", async () => {
  assert.equal(await fixture([[], [Object.assign({},match,{size:0})], [match]]),3);
});
test("transient service errors", async () => {
  assert.equal(await fixture([503,429,[match]]),3);
});
test("ambiguity, permission denial and bounded exhaustion", async () => {
  await assert.rejects(fixture([[match,match]]),/Ambiguous/);
  await assert.rejects(fixture([403]),/403/);
  await assert.rejects(fixture([[{name:"another-artifact",size:20}]]),/did not become visible/);
});
