#!/usr/bin/env node

const fs = require("fs");
const os = require("os");
const path = require("path");

const MANAGED_FILE_MARKER = "<!-- AGENTIC-GRIMOIRE: MANAGED FILE -->";
const BEGIN_SHARED_BLOCK = "<!-- BEGIN AGENTIC-GRIMOIRE SHARED CONTENT -->";
const END_SHARED_BLOCK = "<!-- END AGENTIC-GRIMOIRE SHARED CONTENT -->";
const OLD_BEGIN_INSTALL_BLOCK = "<!-- BEGIN AGENTIC-GRIMOIRE MANAGED BLOCK -->";
const OLD_END_INSTALL_BLOCK = "<!-- END AGENTIC-GRIMOIRE MANAGED BLOCK -->";
const ASCII_BAR = "############################################################";
const BEGIN_MANAGED_SECTION = "# BEGIN AGENTIC-GRIMOIRE MANAGED SECTION";
const END_MANAGED_SECTION = "# END AGENTIC-GRIMOIRE MANAGED SECTION";

const SCRIPT_DIR = __dirname;
const REPO_ROOT = path.resolve(SCRIPT_DIR, "..");
const CLAUDE_SOURCE = path.join(REPO_ROOT, ".claude", "CLAUDE.md");
const CODEX_SOURCE = path.join(REPO_ROOT, ".codex", "AGENTS.md");
const SHARED_DIR = path.join(REPO_ROOT, ".shared-agents");

function warn(message) {
  process.stderr.write(`WARNING: ${message}\n`);
}

function die(message) {
  process.stderr.write(`ERROR: ${message}\n`);
  process.exit(1);
}

function status(label, value) {
  process.stdout.write(`${label}: ${value}\n`);
}

function usage() {
  process.stdout.write(
    [
      "Usage: node scripts/install-agent-docs.js",
      "",
      "Installs repo agent docs into the current device home directory.",
    ].join("\n") + "\n",
  );
}

function detectPlatform() {
  switch (process.platform) {
    case "darwin":
      return "macOS";
    case "linux":
      return os.release().toLowerCase().includes("microsoft") ? "WSL" : "Linux";
    default:
      die(`unsupported platform '${process.platform}'. Only Linux, macOS, and WSL are supported.`);
  }
}

function getTargetHome() {
  const home = os.homedir();
  if (!home || home === "/" || home === ".") {
    die("unable to determine the current user's home directory.");
  }
  return home;
}

function ensurePrereqs() {
  if (!fs.existsSync(CLAUDE_SOURCE)) {
    die(`missing source file: ${CLAUDE_SOURCE}`);
  }
  if (!fs.existsSync(CODEX_SOURCE)) {
    die(`missing source file: ${CODEX_SOURCE}`);
  }
}

function ensureParentDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function readFile(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

function normalizeToLf(text) {
  return text.replace(/\r\n/g, "\n");
}

function detectEol(text) {
  return text.includes("\r\n") ? "\r\n" : "\n";
}

function applyEol(text, eol) {
  return normalizeToLf(text).replace(/\n/g, eol);
}

function ensureTrailingEol(text) {
  return text.endsWith("\n") ? text : `${text}\n`;
}

function appliesToKind(relPath, kind) {
  if (relPath.startsWith(`claude${path.sep}`)) {
    return kind === "claude";
  }
  if (relPath.startsWith(`codex${path.sep}`)) {
    return kind === "codex";
  }
  if (relPath.startsWith(`common${path.sep}`)) {
    return true;
  }
  return true;
}

function listFilesRecursive(rootDir) {
  const files = [];

  function walk(currentDir) {
    const entries = fs.readdirSync(currentDir, { withFileTypes: true });
    entries.sort((a, b) => a.name.localeCompare(b.name));

    for (const entry of entries) {
      const fullPath = path.join(currentDir, entry.name);
      if (entry.isDirectory()) {
        walk(fullPath);
      } else if (entry.isFile()) {
        files.push(fullPath);
      }
    }
  }

  walk(rootDir);
  return files;
}

function buildSharedBlock(kind) {
  if (!fs.existsSync(SHARED_DIR) || !fs.statSync(SHARED_DIR).isDirectory()) {
    return "";
  }

  const matchingFiles = listFilesRecursive(SHARED_DIR).filter((filePath) => {
    const relPath = path.relative(SHARED_DIR, filePath);
    return appliesToKind(relPath, kind);
  });

  if (matchingFiles.length === 0) {
    return "";
  }

  const parts = [BEGIN_SHARED_BLOCK, "<!-- generated from .shared-agents -->"];

  for (const filePath of matchingFiles) {
    const relPath = path.relative(SHARED_DIR, filePath).split(path.sep).join("/");
    let content = readFile(filePath);
    if (!content.endsWith("\n")) {
      content += "\n";
    }

    parts.push("");
    parts.push(`## Shared Instructions: \`${relPath}\``);
    parts.push("");
    parts.push(content.replace(/\n$/, ""));
  }

  parts.push("");
  parts.push(END_SHARED_BLOCK);
  parts.push("");

  return parts.join("\n");
}

function buildDesiredDoc(kind, sourceFile) {
  let content = readFile(sourceFile);
  if (!content.endsWith("\n")) {
    content += "\n";
  }

  const sharedBlock = buildSharedBlock(kind);
  if (!sharedBlock) {
    return content;
  }

  return `${content}\n${sharedBlock}`;
}

function buildManagedFile(desiredText) {
  const normalizedDesired = ensureTrailingEol(normalizeToLf(desiredText));
  return `${MANAGED_FILE_MARKER}\n\n${normalizedDesired}`;
}

function buildManagedSection(desiredText, intendedTarget) {
  const normalizedDesired = ensureTrailingEol(normalizeToLf(desiredText));
  return [
    ASCII_BAR,
    BEGIN_MANAGED_SECTION,
    `# intended target: ${intendedTarget}`,
    ASCII_BAR,
    "",
    normalizedDesired.replace(/\n$/, ""),
    "",
    ASCII_BAR,
    END_MANAGED_SECTION,
    ASCII_BAR,
    "",
  ].join("\n");
}

function splitLines(normalizedText) {
  return normalizedText.split("\n");
}

function findAllBlockRanges(lines, beginMarker, endMarker) {
  const ranges = [];
  let index = 0;

  while (index < lines.length) {
    if (lines[index] !== beginMarker) {
      index += 1;
      continue;
    }

    let endIndex = index + 1;
    while (endIndex < lines.length && lines[endIndex] !== endMarker) {
      endIndex += 1;
    }

    if (endIndex >= lines.length) {
      return { malformed: true, ranges: [] };
    }

    ranges.push([index, endIndex]);
    index = endIndex + 1;
  }

  return { malformed: false, ranges };
}

function stripManagedSections(text) {
  const normalized = normalizeToLf(text);
  const lines = splitLines(normalized);
  const formats = [
    [OLD_BEGIN_INSTALL_BLOCK, OLD_END_INSTALL_BLOCK],
    [BEGIN_MANAGED_SECTION, END_MANAGED_SECTION],
  ];
  const collected = [];

  for (const [beginMarker, endMarker] of formats) {
    const result = findAllBlockRanges(lines, beginMarker, endMarker);
    if (result.malformed) {
      return { malformed: true, found: true, content: normalized };
    }
    for (const range of result.ranges) {
      collected.push(range);
    }
  }

  if (collected.length === 0) {
    return { malformed: false, found: false, content: normalized };
  }

  collected.sort((left, right) => left[0] - right[0]);

  for (let i = 1; i < collected.length; i += 1) {
    if (collected[i][0] <= collected[i - 1][1]) {
      return { malformed: true, found: true, content: normalized };
    }
  }

  const keptLines = [];
  let rangeIndex = 0;

  for (let lineIndex = 0; lineIndex < lines.length; lineIndex += 1) {
    const activeRange = collected[rangeIndex];
    if (activeRange && lineIndex >= activeRange[0] && lineIndex <= activeRange[1]) {
      if (lineIndex === activeRange[1]) {
        rangeIndex += 1;
      }
      continue;
    }
    keptLines.push(lines[lineIndex]);
  }

  let stripped = keptLines.join("\n");
  stripped = stripped.replace(/\n{3,}$/g, "\n\n");

  return { malformed: false, found: true, content: stripped };
}

function prepareAppendCandidate(originalText, desiredText, intendedTarget, eol) {
  const stripped = stripManagedSections(originalText);
  if (stripped.malformed) {
    warn(`found malformed managed block markers in ${intendedTarget}. Appending a fresh managed section.`);
    return null;
  }

  const managedSection = buildManagedSection(desiredText, intendedTarget).replace(/\n$/, "");
  let base = stripped.content;

  if (stripped.found) {
    base = base.replace(/\n*$/, "");
  }

  let normalizedCandidate = base;
  if (normalizedCandidate.length > 0) {
    normalizedCandidate = normalizedCandidate.replace(/\n*$/, "");
    normalizedCandidate = `${normalizedCandidate}\n\n${managedSection}\n`;
  } else {
    normalizedCandidate = `${managedSection}\n`;
  }

  return applyEol(normalizedCandidate, eol);
}

function writeFile(filePath, content) {
  fs.writeFileSync(filePath, content, "utf8");
}

function syncRegularFile(targetFile, desiredText, label, intendedTarget) {
  ensureParentDir(targetFile);

  const desiredManaged = buildManagedFile(desiredText);
  const targetExists = fs.existsSync(targetFile);

  if (!targetExists) {
    writeFile(targetFile, desiredManaged);
    status(label, "updated");
    return;
  }

  let stats;
  try {
    stats = fs.lstatSync(targetFile);
  } catch {
    writeFile(targetFile, desiredManaged);
    status(label, "updated");
    return;
  }

  if (stats.isSymbolicLink()) {
    const linkedContent = readFile(targetFile);
    if (linkedContent === desiredText) {
      status(label, "unchanged");
      return;
    }

    warn(`${targetFile} is a symlink to an unmanaged target. Leaving it unchanged.`);
    status(label, "skipped-conflicting-symlink");
    return;
  }

  const existing = readFile(targetFile);
  const existingNormalized = normalizeToLf(existing);
  const eol = detectEol(existing);
  const desiredManagedForTarget = applyEol(desiredManaged, eol);
  const desiredTextForTarget = applyEol(desiredText, eol);

  if (existing === desiredManagedForTarget || existing === desiredTextForTarget) {
    status(label, "unchanged");
    return;
  }

  if (existingNormalized.split("\n").includes(MANAGED_FILE_MARKER)) {
    writeFile(targetFile, desiredManagedForTarget);
    status(label, "updated");
    return;
  }

  const stripped = stripManagedSections(existing);
  const candidate = prepareAppendCandidate(existing, desiredText, intendedTarget, eol);

  if (candidate && candidate === existing) {
    status(label, "unchanged");
    return;
  }

  if (candidate) {
    writeFile(targetFile, candidate);
    status(label, stripped.found ? "updated" : "appended-with-warning");
    if (!stripped.found) {
      warn(`${targetFile} already existed. Preserved original content and appended a managed section at the bottom.`);
    }
    return;
  }

  const fallbackSection = applyEol(buildManagedSection(desiredText, intendedTarget), eol).replace(/(?:\r?\n)$/, "");
  let fallbackContent = existing;
  if (fallbackContent.length > 0) {
    fallbackContent = fallbackContent.replace(/(?:\r?\n)*$/, "");
    fallbackContent = `${fallbackContent}${eol}${eol}${fallbackSection}${eol}`;
  } else {
    fallbackContent = `${fallbackSection}${eol}`;
  }

  writeFile(targetFile, fallbackContent);
  warn(`${targetFile} already existed. Preserved original content and appended a managed section at the bottom.`);
  status(label, "appended-with-warning");
}

function install(targetHome = getTargetHome()) {
  const platform = detectPlatform();
  ensurePrereqs();

  const claudeDesired = buildDesiredDoc("claude", CLAUDE_SOURCE);
  const codexDesired = buildDesiredDoc("codex", CODEX_SOURCE);
  const homeClaudeFile = path.join(targetHome, ".claude", "CLAUDE.md");
  const homeCodexFile = path.join(targetHome, ".codex", "AGENTS.md");

  process.stdout.write(`Platform: ${platform}\n`);
  process.stdout.write(`Target home: ${targetHome}\n`);

  syncRegularFile(homeClaudeFile, claudeDesired, "~/.claude/CLAUDE.md", "~/.claude/CLAUDE.md");
  syncRegularFile(homeCodexFile, codexDesired, "~/.codex/AGENTS.md", "~/.codex/AGENTS.md");
}

if (require.main === module) {
  if (process.argv[2] === "--help") {
    usage();
    process.exit(0);
  }

  install();
}

module.exports = {
  buildDesiredDoc,
  buildManagedFile,
  buildManagedSection,
  install,
  stripManagedSections,
};
