#!/usr/bin/env node
/**
 * Record one run of a JavaScript or TypeScript workflow the way a time-travel debugger replays
 * it: one step for every line, call, await, resume and return in the watched files, each with
 * the variables that changed since that frame's previous step, printed the way console.log
 * would show them.
 *
 *   node record_js.mjs --root . --watch src lib \
 *       --entry "tests/cart.test.ts::checkout in SG" --out .codewalk/recordings/checkout.json \
 *       [--staging .codewalk/staging/retry]
 *
 * The entry is a driver script, or `<test file>::<test name>` run by the project's vitest or
 * jest. Every Node process the run starts opens the inspector (NODE_OPTIONS=--inspect-brk); this
 * script attaches to each over the Chrome DevTools Protocol, puts a breakpoint on every line of
 * the watched files, and records each pause as record_py.py records a line event. TypeScript
 * lines come back through each script's source map. Output shape: references/page-format.md.
 */

import { spawn } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { inspect, parseArgs } from "node:util";

const GONE = -1; // a variable that left the frame since its previous step
const INSPECT = { depth: 4, maxArrayLength: 50, maxStringLength: Infinity, breakLength: 72, compact: 3 };
const SOURCE_EXTENSIONS = [".js", ".mjs", ".cjs", ".jsx", ".ts", ".mts", ".cts", ".tsx"];
const TEST_FILE = /(\.(test|spec)\.[cm]?[jt]sx?$)|(__tests__\/)/;
const INSPECTOR_CHATTER = /^(Debugger listening on |For help, see: |Debugger attached\.|Waiting for the debugger to disconnect)/;

async function main() {
  const { values: flags, positionals } = parseArgs({
    options: {
      root: { type: "string" },
      watch: { type: "string", multiple: true },
      entry: { type: "string" },
      out: { type: "string" },
      staging: { type: "string" },
      "max-steps": { type: "string", default: "50000" },
    },
    allowPositionals: true, // `--watch src lib` leaves `lib` as a positional
  });
  if (!flags.root || !flags.watch || !flags.entry || !flags.out) {
    console.error("usage: record_js.mjs --root <dir> --watch <paths…> --entry <driver | file::test> --out <file> [--staging <dir>]");
    return 2;
  }
  const root = path.resolve(flags.root);
  const tree = new Tree(root, flags.staging ? path.resolve(root, flags.staging) : null);
  const out = path.resolve(flags.out);
  const recording = new Recording(Number(flags["max-steps"]));
  const command = commandFor(tree, flags.entry);
  const exit = await runAttached(command, tree, tree.watchedPrefixes([...flags.watch, ...positionals]), recording);

  mkdirSync(path.dirname(out), { recursive: true });
  writeFileSync(out, JSON.stringify({
    version: 1,
    language: recording.frames.some((f) => /\.[cm]?tsx?$/.test(f.path)) ? "typescript" : "javascript",
    entry: { kind: command.kind, target: flags.entry },
    exit,
    truncated: recording.truncated,
    staging: tree.staging ? path.relative(root, tree.staging).split(path.sep).join("/") : null,
    staged: tree.staged(),
    frames: recording.frames,
    steps: recording.steps,
    values: recording.values,
  }));
  console.log(`${out}: ${recording.steps.length} steps in ${recording.frames.length} calls; `
    + `exit ${exit.ok ? "ok" : "FAILED"} (${exit.detail})${recording.truncated ? "; TRUNCATED at --max-steps" : ""}`);
  return 0;
}

// ---- what to run ------------------------------------------------------------------------------

/** The node arguments for the entry: a test through the project's runner, or a driver. */
function commandFor(tree, entry) {
  const [file, testName] = entry.split("::");
  if (testName !== undefined || TEST_FILE.test(file)) {
    const runner = testRunnerOf(tree.root);
    const filter = testName === undefined ? [] : ["-t", testName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")];
    const args = runner === "vitest"
      ? [binOf(tree.root, "vitest"), "run", file, ...filter, "--no-file-parallelism"]
      : [binOf(tree.root, "jest"), file, ...filter, "--runInBand"];
    return { kind: "test", runner, args, nodeOptions: [] };
  }
  const typescript = /\.[cm]?tsx?$/.test(file);
  const loader = !typescript ? [] : hasPackage(tree.root, "tsx") ? ["--import", "tsx"] : ["--experimental-strip-types"];
  // Staging rides on Node's resolver, so it reaches drivers; vitest and jest resolve modules
  // themselves (references/staging.md).
  const staging = tree.staging ? [`--import=data:text/javascript,${encodeURIComponent(stagingHook(tree))}`] : [];
  return { kind: "driver", runner: "node", args: [...loader, file], nodeOptions: staging };
}

function testRunnerOf(root) {
  if (hasPackage(root, "vitest")) return "vitest";
  if (hasPackage(root, "jest")) return "jest";
  throw new Error(`no vitest or jest installed under ${root}; write a driver instead`);
}

function hasPackage(root, name) {
  try {
    createRequire(path.join(root, "package.json")).resolve(`${name}/package.json`);
    return true;
  } catch {
    return false;
  }
}

/** The runner's own CLI script, run with this node so the inspector flag reaches it. */
function binOf(root, name) {
  const manifest = createRequire(path.join(root, "package.json")).resolve(`${name}/package.json`);
  const { bin } = JSON.parse(readFileSync(manifest, "utf8"));
  return path.join(path.dirname(manifest), typeof bin === "string" ? bin : bin[name]);
}

/** A resolve hook: a staged file wins over the project's file at the same path, and a
 * staged-only file resolves as if it sat in the project. */
function stagingHook(tree) {
  return `
import { registerHooks } from "node:module";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
const root = ${JSON.stringify(tree.root)}, staging = ${JSON.stringify(tree.staging)};
const endings = ["", ".ts", ".mts", ".tsx", ".js", ".mjs", ".cjs", "/index.ts", "/index.js"];
const inside = (file, dir) => file.startsWith(dir + path.sep);
const twin = (file) => {
  if (!inside(file, root) || inside(file, staging)) return null;
  const staged = path.join(staging, path.relative(root, file));
  return existsSync(staged) ? staged : null;
};
const asProject = (file) => inside(file, staging) ? path.join(root, path.relative(staging, file)) : file;
registerHooks({
  resolve(specifier, context, nextResolve) {
    try {
      const found = nextResolve(specifier, context);
      const staged = found.url.startsWith("file:") ? twin(fileURLToPath(found.url)) : null;
      return staged ? { ...found, url: pathToFileURL(staged).href } : found;
    } catch (error) {
      if (!specifier.startsWith(".") || !context.parentURL?.startsWith("file:")) throw error;
      const parent = asProject(fileURLToPath(context.parentURL));
      const wanted = path.resolve(path.dirname(parent), specifier);
      for (const ending of endings) {
        const staged = twin(wanted + ending);
        if (staged) return { url: pathToFileURL(staged).href, shortCircuit: true };
      }
      return nextResolve(specifier, { ...context, parentURL: pathToFileURL(parent).href });
    }
  },
});`;
}

// ---- run it, attached to every node process it starts -------------------------------------------

async function runAttached(command, tree, watched, recording) {
  const env = {
    ...process.env,
    NODE_OPTIONS: [process.env.NODE_OPTIONS, "--inspect-brk=127.0.0.1:0", ...command.nodeOptions].filter(Boolean).join(" "),
  };
  const child = spawn(process.execPath, command.args, { cwd: tree.root, env, stdio: ["inherit", "inherit", "pipe"] });
  const sessions = [];
  let pending = "";
  child.stderr.on("data", (chunk) => {
    pending += chunk;
    const lines = pending.split("\n");
    pending = lines.pop();
    for (const line of lines) {
      const listening = /Debugger listening on (ws:\/\/\S+)/.exec(line);
      if (listening) sessions.push(new Session(listening[1], tree, watched, recording).start());
      else if (!INSPECTOR_CHATTER.test(line)) process.stderr.write(line + "\n");
    }
  });
  const code = await new Promise((resolve) => child.on("exit", (exitCode, signal) => resolve(exitCode ?? signal)));
  await Promise.allSettled(sessions);
  return { ok: code === 0, detail: `${command.runner} exit code ${code}` };
}

// ---- one inspected process ----------------------------------------------------------------------

/** One Node process over the Chrome DevTools Protocol. `start` resolves when it disconnects. */
class Session {
  #socket;
  #nextId = 0;
  #replies = new Map();
  #scripts = new Map(); // scriptId -> Script, watched scripts only
  #arming = new Map(); // scriptId -> the promise of its breakpoints being set
  #defaultContexts = new Set();
  #tracker;
  #tree;
  #watched;
  #recording;

  constructor(url, tree, watched, recording) {
    this.#socket = new WebSocket(url);
    this.#tree = tree;
    this.#watched = watched;
    this.#recording = recording;
    this.#tracker = new Tracker(recording);
  }

  async start() {
    await new Promise((resolve, reject) => {
      this.#socket.onopen = resolve;
      this.#socket.onerror = reject;
    });
    const closed = new Promise((resolve) => { this.#socket.onclose = resolve; });
    this.#socket.onmessage = (event) => this.#receive(JSON.parse(event.data));
    await this.#send("Runtime.enable");
    await this.#send("Debugger.enable");
    await this.#send("Debugger.setBlackboxPatterns", { patterns: [blackboxPattern(this.#watched)] });
    await this.#send("Debugger.setPauseOnExceptions", { state: "all" });
    // A watched script's breakpoints are set as soon as it is parsed. Node's own loaders also
    // pause it before it runs, until they are set; a `vm.Script` (jest) runs on, which only
    // matters for calls its module body makes, and module bodies are not recorded.
    await this.#send("Debugger.setInstrumentationBreakpoint", { instrumentation: "beforeScriptExecution" });
    await this.#send("Runtime.runIfWaitingForDebugger");
    await closed;
    this.#tracker.finish();
  }

  #send(method, params = {}) {
    const id = ++this.#nextId;
    return new Promise((resolve) => {
      this.#replies.set(id, resolve);
      this.#socket.send(JSON.stringify({ id, method, params }));
    });
  }

  #receive(message) {
    if (message.id !== undefined) {
      this.#replies.get(message.id)?.(message.result ?? { error: message.error });
      this.#replies.delete(message.id);
    } else if (message.method === "Debugger.scriptParsed") {
      this.#arm(message.params).catch((error) => console.error(`record_js: ${error.stack}`));
    } else if (message.method === "Debugger.paused") {
      this.#onPaused(message.params).catch((error) => {
        console.error(`record_js: ${error.stack}`);
        this.#send("Debugger.resume");
      });
    } else if (message.method === "Runtime.executionContextCreated" && message.params.context.auxData?.isDefault) {
      this.#defaultContexts.add(message.params.context.id);
    } else if (message.method === "Runtime.executionContextDestroyed" && this.#defaultContexts.has(message.params.executionContextId)) {
      this.#socket.close(); // the process is exiting; let it go
    }
  }

  async #onPaused(paused) {
    if (paused.reason === "instrumentation") {
      await this.#arm(paused.data);
      return this.#send("Debugger.resume");
    }
    const top = paused.callFrames[0];
    if (this.#recording.full || !this.#isWatchedFunction(top)) return this.#send("Debugger.resume");
    const stack = [];
    for (const callFrame of [...paused.callFrames].reverse()) {
      if (!this.#isWatchedFunction(callFrame)) continue;
      const at = await this.#place(callFrame);
      if (at.ownCode) stack.push(at);
    }
    if (stack.at(-1)?.callFrame !== top) return this.#send("Debugger.resume");
    const printed = await this.#variables(top);
    let kind = "line";
    if (paused.reason === "exception" || paused.reason === "promiseRejection") {
      kind = "raise";
      printed["(raised)"] = firstLine(await this.#print(paused.data));
    } else if (top.returnValue) {
      kind = "return";
      printed["(return value)"] = await this.#print(top.returnValue);
    }
    this.#tracker.step(stack, kind, printed);
    if (this.#recording.full) {
      await this.#send("Debugger.setBreakpointsActive", { active: false });
      await this.#send("Debugger.setPauseOnExceptions", { state: "none" });
    }
    return this.#send("Debugger.resume");
  }

  /** A watched script's breakpoints: one per source line, plus every return point. */
  #arm(parsed) {
    if (!this.#arming.has(parsed.scriptId)) this.#arming.set(parsed.scriptId, this.#setBreakpoints(parsed));
    return this.#arming.get(parsed.scriptId);
  }

  async #setBreakpoints({ scriptId, url, sourceMapURL }) {
    const file = fileOfUrl(url);
    if (!file || !isWatched(file, this.#watched)) return;
    const script = new Script(scriptId, file, this.#tree.projectPath(file), loadSourceMap(url, sourceMapURL));
    this.#scripts.set(scriptId, script);
    const { locations = [] } = await this.#send("Debugger.getPossibleBreakpoints", {
      start: { scriptId, lineNumber: 0, columnNumber: 0 },
    });
    const taken = new Set();
    for (const location of locations) {
      const key = `${script.line(location)}${location.type === "return" ? ":return" : ""}`;
      if (taken.has(key)) continue;
      taken.add(key);
      await this.#send("Debugger.setBreakpoint", { location });
    }
  }

  #isWatchedFunction(callFrame) {
    return this.#scripts.has(callFrame.location.scriptId) && callFrame.scopeChain.some((scope) => scope.type === "local");
  }

  /** A call frame as the tracker sees it: which function, where, its source range, and whether
   * it is the project's own code — not a module wrapper (vite's, CommonJS's, jest's: they take
   * `__filename` and `__dirname`, and are what a module body is in Python) and not code a
   * transform generated (no line in the source map). */
  async #place(callFrame) {
    const script = this.#scripts.get(callFrame.location.scriptId);
    const at = callFrame.functionLocation ?? callFrame.location;
    const key = `${at.scriptId}:${at.lineNumber}:${at.columnNumber}`;
    if (!script.ranges.has(key)) {
      const { locations = [] } = await this.#send("Debugger.getPossibleBreakpoints", { start: at, restrictToFunction: true });
      const lines = locations.filter((location) => !script.isGenerated(location)).map((location) => script.line(location));
      const local = callFrame.scopeChain.find((scope) => scope.type === "local");
      const { result = [] } = await this.#send("Runtime.getProperties", { objectId: local.object.objectId, ownProperties: true });
      const names = new Set(result.map((property) => property.name));
      script.ranges.set(key, {
        start: script.line(at),
        end: Math.max(script.line(at), ...lines),
        first: lines[0] ?? script.line(at),
        ownCode: !script.isGenerated(at, callFrame.functionName)
          && !(names.has("__filename") && names.has("__dirname"))
          && callFrame.functionName !== "<static_initializer>", // a class body: runs once, at import
      });
    }
    const range = script.ranges.get(key);
    const owner = callFrame.this?.type === "object" && !["global", "Window", "Object"].includes(callFrame.this.className)
      ? `${callFrame.this.className}.` : "";
    return {
      key,
      callFrame,
      ownCode: range.ownCode,
      line: script.line(callFrame.location),
      first: range.first,
      describe: (parent) => ({
        function: `${path.parse(script.projectPath).name}.${owner}${callFrame.functionName || "(anonymous)"}`,
        path: script.projectPath,
        start: range.start,
        end: range.end,
        parent,
        task: "main",
      }),
    };
  }

  /** The paused frame's own variables (block scopes in, closures out), read off its scope
   * objects, with `this` spread into one `this.<field>` entry each (private `#fields` too).
   * Nothing is evaluated inside the frame: V8 can crash evaluating in some (a class static
   * block). A `let` or `const` not yet reached has no value, so it is left out, as Python
   * leaves out an unassigned local; so is a getter, which only a call could read. */
  async #variables(callFrame) {
    const printed = {};
    if (callFrame.this?.type === "object" && callFrame.this.subtype !== "null" && !["global", "Window"].includes(callFrame.this.className)) {
      const { result = [], privateProperties = [] } = await this.#send("Runtime.getProperties", { objectId: callFrame.this.objectId, ownProperties: true });
      for (const { name, value } of [...result, ...privateProperties]) {
        if (value !== undefined) printed[`this.${name}`] = await this.#print(value);
      }
    }
    for (const scope of callFrame.scopeChain) {
      if (!["block", "catch", "local"].includes(scope.type)) break;
      const { result = [] } = await this.#send("Runtime.getProperties", { objectId: scope.object.objectId, ownProperties: true });
      for (const { name, value } of result) {
        if (name in printed || name === "arguments" || value === undefined) continue;
        printed[name] = await this.#print(value);
      }
      if (scope.type === "local") break;
    }
    return printed;
  }

  /** A protocol value as console.log would print it. */
  async #print(remote) {
    if (!remote) return "undefined";
    if (remote.objectId) {
      const { result } = await this.#send("Runtime.callFunctionOn", {
        objectId: remote.objectId,
        functionDeclaration: `function () { return globalThis.process.getBuiltinModule("node:util").inspect(this, ${JSON.stringify(INSPECT)}); }`,
        returnByValue: true,
        silent: true,
      });
      return result?.value ?? remote.description ?? String(remote.type);
    }
    if (remote.unserializableValue !== undefined) return remote.unserializableValue;
    return inspect(remote.value, INSPECT);
  }
}

// ---- from protocol pauses to frames and steps ---------------------------------------------------

/** Turns each pause's stack of watched frames into frames and steps, the way record_py.py's
 * sys.monitoring events do. The protocol reports only stacks, so calls, returns, awaits and
 * resumes are read off how the stack changed since the previous pause. */
class Tracker {
  #live = []; // the watched frames on the stack, bottom first: { key, frame, line, returned, raised }
  #suspended = []; // frames that left the stack mid-function: awaiting, resumed later
  #recording;

  constructor(recording) {
    this.#recording = recording;
  }

  step(stack, kind, printed) {
    const live = this.#live;
    let kept = 0;
    while (kept < live.length && kept < stack.length && live[kept].key === stack[kept].key && !live[kept].returned) kept++;
    for (const gone of live.splice(kept).reverse()) this.#leave(gone);
    const variables = Object.fromEntries(Object.entries(printed).filter(([name]) => !name.startsWith("(")));
    for (let i = kept; i < stack.length; i++) this.#enter(stack[i], live.at(-1)?.frame ?? -1, i === stack.length - 1 ? variables : null);
    const top = live.at(-1);
    const entered = kept < stack.length;
    if (!entered || kind !== "line") this.#recording.add(top.frame, stack.at(-1).line, kind, printed);
    top.line = stack.at(-1).line;
    top.returned = kind === "return";
    top.raised = kind === "raise" || (top.raised && kind !== "line");
  }

  /** A frame left the stack without returning: it raised, or it is awaiting. */
  #leave(gone) {
    if (gone.returned) return;
    if (gone.raised) return this.#recording.add(gone.frame, gone.line, "unwind", null);
    this.#recording.add(gone.frame, gone.line, "await", null);
    this.#suspended.push(gone);
  }

  /** The run ended: a frame that raised and never ran again was unwound by its exception. */
  finish() {
    for (const entry of this.#live.reverse()) if (entry.raised) this.#recording.add(entry.frame, entry.line, "unwind", null);
    this.#live = [];
  }

  /** A frame joined the stack: a fresh call, or a suspended frame resuming past its first line. */
  #enter(at, parent, printed) {
    const index = at.line === at.first ? -1 : this.#suspended.findLastIndex((s) => s.key === at.key);
    const resumed = index >= 0 ? this.#suspended.splice(index, 1)[0] : null;
    const entry = resumed ?? { key: at.key, frame: this.#recording.addFrame(at.describe(parent)), line: at.line };
    entry.returned = false;
    entry.raised = false;
    this.#live.push(entry);
    this.#recording.add(entry.frame, at.line, resumed ? "resume" : "call", printed);
  }
}

class Recording {
  frames = [];
  steps = [];
  values = [];
  truncated = false;
  #maxSteps;
  #valueIndex = new Map();
  #printed = new Map(); // frame -> its variables at its last step

  constructor(maxSteps) {
    this.#maxSteps = maxSteps;
  }

  get full() {
    return this.steps.length >= this.#maxSteps;
  }

  addFrame(frame) {
    this.frames.push(frame);
    this.#printed.set(this.frames.length - 1, {});
    return this.frames.length - 1;
  }

  /** One step; `printed` null means the step saw no variables (an await or unwind). */
  add(frame, line, kind, printed) {
    if (this.full) {
      this.truncated = true;
      return;
    }
    const changed = {};
    if (printed) {
      const before = this.#printed.get(frame);
      for (const [name, text] of Object.entries(printed)) if (before[name] !== text) changed[name] = this.#value(text);
      for (const name of Object.keys(before)) if (!(name in printed)) changed[name] = GONE;
      this.#printed.set(frame, printed);
    }
    this.steps.push([frame, line, kind, changed]);
  }

  #value(text) {
    if (!this.#valueIndex.has(text)) {
      this.#valueIndex.set(text, this.values.length);
      this.values.push(text);
    }
    return this.#valueIndex.get(text);
  }
}

// ---- files, staging and source maps -------------------------------------------------------------

/** The project root and, for a prototype, the staging folder mirroring its paths. Every path a
 * recording names is the project path, staged or not (references/staging.md). */
class Tree {
  constructor(root, staging) {
    this.root = root;
    this.staging = staging;
  }

  staged() {
    if (!this.staging) return [];
    return listFiles(this.staging)
      .filter((file) => SOURCE_EXTENSIONS.includes(path.extname(file)))
      .map((file) => path.relative(this.staging, file).split(path.sep).join("/"))
      .sort();
  }

  projectPath(file) {
    const base = this.staging && file.startsWith(this.staging + path.sep) ? this.staging : this.root;
    return path.relative(base, file).split(path.sep).join("/");
  }

  /** Each watched path under the root and under staging. A folder ends in a separator, so
   * `src/up` never matches `src/upload.ts`. */
  watchedPrefixes(watch) {
    const bases = this.staging ? [this.root, this.staging] : [this.root];
    return bases.flatMap((base) => watch.map((entry) => {
      const full = path.resolve(base, entry);
      return existsSync(full) && statSync(full).isDirectory() ? full + path.sep : full;
    }));
  }
}

class Script {
  ranges = new Map(); // function key -> { start, end, first } in source lines

  constructor(id, file, projectPath, sourceMap) {
    this.id = id;
    this.file = file;
    this.projectPath = projectPath;
    this.sourceMap = sourceMap;
  }

  /** A protocol location (0-based, in the code that ran) as a 1-based source line. */
  line({ lineNumber, columnNumber = 0 }) {
    return this.sourceMap?.originalLine(lineNumber, columnNumber) ?? lineNumber + 1;
  }

  /** A transform wrote this function: the source map maps nothing on its line back to the
   * source, or — for the unnamed helpers transforms add, like vite's export getters — nothing
   * starts at its own column. */
  isGenerated({ lineNumber, columnNumber = 0 }, functionName = null) {
    if (this.sourceMap === null) return false;
    if (this.sourceMap.originalLine(lineNumber, columnNumber) === null) return true;
    if (functionName?.startsWith("__")) return true; // a transform's helper: esbuild's __name, tsc's __awaiter
    return ["", "get"].includes(functionName) && !this.sourceMap.startsAt(lineNumber, columnNumber);
  }
}

function loadSourceMap(url, sourceMapURL) {
  if (!sourceMapURL) return null;
  try {
    let text;
    if (sourceMapURL.startsWith("data:")) {
      const comma = sourceMapURL.indexOf(",");
      const body = sourceMapURL.slice(comma + 1);
      text = sourceMapURL.slice(0, comma).endsWith(";base64") ? Buffer.from(body, "base64").toString("utf8") : decodeURIComponent(body);
    } else {
      const file = fileOfUrl(url);
      text = readFileSync(path.resolve(path.dirname(file), sourceMapURL), "utf8");
    }
    return new SourceMap(JSON.parse(text).mappings);
  } catch {
    return null; // lines fall back to the code that ran
  }
}

/** Source map v3, lines only: for each generated line, the segments mapping it back. */
class SourceMap {
  #lines;

  constructor(mappings) {
    this.#lines = decodeMappings(mappings);
  }

  startsAt(line, column) {
    return (this.#lines[line] ?? []).some((segment) => segment.column === column);
  }

  originalLine(line, column) {
    const segments = this.#lines[line];
    if (!segments?.length) return null;
    let best = segments[0];
    for (const segment of segments) if (segment.column <= column) best = segment;
    return best.sourceLine + 1;
  }
}

const BASE64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

function decodeMappings(mappings) {
  const lines = [];
  let sourceLine = 0;
  for (const text of mappings.split(";")) {
    const segments = [];
    let column = 0;
    for (const segment of text.split(",")) {
      if (!segment) continue;
      const fields = decodeVlq(segment);
      column += fields[0];
      if (fields.length >= 4) {
        sourceLine += fields[2];
        segments.push({ column, sourceLine });
      }
    }
    lines.push(segments);
  }
  return lines;
}

function decodeVlq(segment) {
  const fields = [];
  let value = 0;
  let shift = 0;
  for (const char of segment) {
    const digit = BASE64.indexOf(char);
    value += (digit & 31) * 2 ** shift;
    if (digit & 32) {
      shift += 5;
    } else {
      fields.push(value % 2 ? -Math.floor(value / 2) : value / 2);
      value = 0;
      shift = 0;
    }
  }
  return fields;
}

// ---- small helpers ------------------------------------------------------------------------------

function fileOfUrl(url) {
  if (url.startsWith("file://")) return fileURLToPath(url);
  return path.isAbsolute(url) ? url : null; // jest names its scripts by plain path
}

function isWatched(file, watched) {
  return watched.some((prefix) => file === prefix || (prefix.endsWith(path.sep) && file.startsWith(prefix)));
}

/** Every script outside the watched paths, named by path (jest) or file URL, as a regex: no
 * exception pauses in library code. */
function blackboxPattern(watched) {
  const escape = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const forms = watched.flatMap((prefix) => [prefix, pathToFileURL(prefix).href]);
  return `^(?!(${forms.map(escape).join("|")}))`;
}

function listFiles(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(dir, entry.name);
    return entry.isDirectory() ? listFiles(full) : [full];
  });
}

function firstLine(text) {
  return text.split("\n")[0];
}

process.exitCode = await main();
