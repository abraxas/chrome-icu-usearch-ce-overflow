"use strict";

// In-tree StringSearchTest::TestCEIndexOverflow (ICU-23568 / bug 574025697).
// U+FDFA expands to 18 primary CEs under the search collator.
// 119304647 * 18 == INT32_MAX - 1. The 65 "A" pattern is past that index.
// Newlines are shaping breaks (InlineItem::kControl). They stay inside one
// block, so window.find still runs one usearch over the whole corpus.
const REPS = 119304647;
const PATTERN_LEN = 65;
const SMOKE_REPS = 5000;
const CHUNK = 4096;
const PATTERN = "A".repeat(PATTERN_LEN);
const UNIT = "\uFDFA".repeat(CHUNK);

function beacon(payload) {
  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/beacon", false);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.send(JSON.stringify(payload));
}

function breakCount(reps) {
  if (reps <= CHUNK) {
    return 0;
  }
  return Math.floor((reps - 1) / CHUNK);
}

function build(reps) {
  const parts = [];
  let done = 0;
  while (done + CHUNK < reps) {
    parts.push(UNIT);
    parts.push("\n");
    done += CHUNK;
  }
  parts.push("\uFDFA".repeat(reps - done));
  parts.push(PATTERN);
  parts.push("!");
  return parts.join("");
}

function search(reps, phase) {
  const corpus = document.getElementById("corpus");
  const status = document.getElementById("status");
  const expect = reps + breakCount(reps);
  status.textContent = phase + " build";
  beacon({ phase: phase + "-build", reps: reps, expect: expect });
  const built = build(reps);
  beacon({
    phase: phase + "-built",
    reps: reps,
    n: built.length,
    expect: expect,
  });
  corpus.textContent = built;
  const node = corpus.firstChild;
  beacon({
    phase: phase + "-assigned",
    reps: reps,
    n: node ? node.length : 0,
  });
  const sel = window.getSelection();
  sel.removeAllRanges();
  if (node) {
    const range = document.createRange();
    range.setStart(node, 0);
    range.collapse(true);
    sel.addRange(range);
  }
  beacon({ phase: phase + "-begin", reps: reps, expect: expect });
  const t0 = performance.now();
  let found = false;
  let error = "";
  try {
    found = window.find(PATTERN, false, false, true);
  } catch (err) {
    error = String(err);
  }
  const ms = performance.now() - t0;
  const anchor = sel.anchorOffset;
  const focus = sel.focusOffset;
  const same = Boolean(node) && sel.anchorNode === node && sel.focusNode === node;
  const lo = Math.min(anchor, focus);
  const hi = Math.max(anchor, focus);
  const offsetOk = Boolean(
    found && same && lo === expect && hi === expect + PATTERN_LEN
  );
  status.textContent = phase + " " + String(offsetOk);
  return {
    reps: reps,
    found: found,
    anchor: anchor,
    focus: focus,
    same: same,
    expect: expect,
    offsetOk: offsetOk,
    ms: ms,
    n: node ? node.length : 0,
    error: error,
  };
}

function main() {
  beacon({ phase: "start" });
  try {
    const smoke = search(SMOKE_REPS, "smoke");
    beacon(Object.assign({ phase: "smoke" }, smoke));
    if (!smoke.offsetOk) {
      beacon({ phase: "done", ok: false, reason: "smoke-failed" });
      return;
    }
    corpusDrop();
    const full = search(REPS, "full");
    beacon(Object.assign({ phase: "full" }, full));
    beacon({
      phase: "done",
      ok: full.offsetOk,
      reason: full.offsetOk ? "match" : "no-match",
    });
  } catch (err) {
    beacon({ phase: "done", ok: false, reason: "exception", error: String(err) });
  }
}

function corpusDrop() {
  const corpus = document.getElementById("corpus");
  corpus.textContent = "";
}

main();
