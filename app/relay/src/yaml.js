/**
 * Minimal YAML subset parser for org policy documents.
 *
 * The relay runs as a zero-dependency Worker, so it cannot pull in a YAML
 * library, but org policy has to be YAML: it is the same `githubai.yml`
 * schema repos already use (see docs/configuration.md), and forcing operators
 * to learn a second format would violate "config over code".
 *
 * Supported: block mappings, block sequences (including `- key: value` items),
 * flow sequences/mappings, quoted and plain scalars, block scalars (| > with
 * - and + chomping), comments, and a single leading `---`.
 *
 * Deliberately unsupported — these throw `YamlError` rather than being
 * silently misread, because a policy document that parses to the wrong thing
 * is worse than one that fails loudly: anchors, aliases, merge keys, explicit
 * tags, multi-document streams, and tab indentation.
 *
 * Booleans follow PyYAML's YAML 1.1 behaviour (`yes`/`no`/`on`/`off` are
 * booleans) so a file means the same thing here and in actions/load-config.
 */

const MAX_DEPTH = 20;

export class YamlError extends Error {
  constructor(message, line) {
    super(line == null ? message : `${message} (line ${line + 1})`);
    this.name = "YamlError";
    this.line = line;
  }
}

/** Parse a YAML subset document. Returns null for an empty document. */
export function parseYaml(text) {
  if (typeof text !== "string") throw new YamlError("expected a string");
  const lines = text.replace(/^﻿/, "").replace(/\r\n?/g, "\n").split("\n");
  const cur = { lines, i: 0 };

  skipBlanks(cur);
  if (cur.i < lines.length && lines[cur.i].trim() === "---") cur.i++;

  const value = parseNode(cur, 0, 0);

  skipBlanks(cur);
  if (cur.i < lines.length) {
    const rest = lines[cur.i].trim();
    if (rest === "---" || rest === "...") {
      throw new YamlError("multi-document YAML is not supported", cur.i);
    }
    throw new YamlError(`unexpected content: ${rest.slice(0, 40)}`, cur.i);
  }
  return value;
}

function skipBlanks(cur) {
  while (cur.i < cur.lines.length && isSkippable(cur.lines[cur.i])) cur.i++;
}

function isSkippable(line) {
  const trimmed = line.trim();
  return trimmed === "" || trimmed.startsWith("#");
}

function indentOf(line, lineNo) {
  let n = 0;
  while (n < line.length && line[n] === " ") n++;
  if (line[n] === "\t") throw new YamlError("tab indentation is not supported", lineNo);
  return n;
}

/** Parse whatever node starts at or after the cursor, at >= minIndent. */
function parseNode(cur, minIndent, depth) {
  if (depth > MAX_DEPTH) throw new YamlError("document nested too deeply", cur.i);
  skipBlanks(cur);
  if (cur.i >= cur.lines.length) return null;
  const line = cur.lines[cur.i];
  const indent = indentOf(line, cur.i);
  if (indent < minIndent) return null;
  const content = line.slice(indent);
  return content === "-" || content.startsWith("- ")
    ? parseSequence(cur, indent, depth)
    : parseMapping(cur, indent, depth);
}

function parseMapping(cur, indent, depth) {
  const map = {};
  while (true) {
    skipBlanks(cur);
    if (cur.i >= cur.lines.length) break;
    const lineNo = cur.i;
    const line = cur.lines[lineNo];
    const lineIndent = indentOf(line, lineNo);
    if (lineIndent < indent) break;
    if (lineIndent > indent) throw new YamlError("unexpected indentation", lineNo);

    const content = line.slice(indent);
    if (content === "-" || content.startsWith("- ")) {
      throw new YamlError("sequence item where a mapping key was expected", lineNo);
    }
    const split = splitKey(content, lineNo);
    if (!split) throw new YamlError(`expected 'key: value', got: ${content.slice(0, 40)}`, lineNo);

    const { key, rest } = split;
    if (Object.prototype.hasOwnProperty.call(map, key)) {
      throw new YamlError(`duplicate key '${key}'`, lineNo);
    }
    cur.i++;

    if (rest === "") {
      map[key] = parseNode(cur, indent + 1, depth + 1);
    } else if (rest[0] === "|" || rest[0] === ">") {
      map[key] = parseBlockScalar(cur, indent, rest, lineNo);
    } else {
      map[key] = parseScalar(rest, lineNo);
    }
  }
  return map;
}

function parseSequence(cur, indent, depth) {
  const items = [];
  while (true) {
    skipBlanks(cur);
    if (cur.i >= cur.lines.length) break;
    const lineNo = cur.i;
    const line = cur.lines[lineNo];
    const lineIndent = indentOf(line, lineNo);
    if (lineIndent < indent) break;
    if (lineIndent > indent) throw new YamlError("unexpected indentation", lineNo);

    const content = line.slice(indent);
    if (content !== "-" && !content.startsWith("- ")) break;

    const after = content.slice(1);
    const pad = after.length - after.replace(/^ +/, "").length;
    const rest = after.slice(pad);

    if (rest === "") {
      cur.i++;
      items.push(parseNode(cur, indent + 1, depth + 1));
      continue;
    }

    // Re-indent the item in place so `- key: value` (with sibling keys on the
    // following lines) parses as an ordinary mapping starting under the dash.
    const itemIndent = indent + 1 + pad;
    cur.lines[lineNo] = " ".repeat(itemIndent) + rest;
    if (rest[0] === "|" || rest[0] === ">") {
      throw new YamlError("block scalar directly in a sequence is not supported", lineNo);
    }
    items.push(
      splitKey(rest, lineNo)
        ? parseMapping(cur, itemIndent, depth + 1)
        : (cur.i++, parseScalar(rest, lineNo)),
    );
  }
  return items;
}

function parseBlockScalar(cur, parentIndent, header, lineNo) {
  const match = /^([|>])([-+]?)(\d*)\s*(#.*)?$/.exec(header.trim());
  if (!match) throw new YamlError(`unsupported block scalar header: ${header}`, lineNo);
  const [, style, chomp, explicitIndent] = match;

  const raw = [];
  while (cur.i < cur.lines.length) {
    const line = cur.lines[cur.i];
    if (line.trim() !== "" && indentOf(line, cur.i) <= parentIndent) break;
    raw.push(line);
    cur.i++;
  }
  while (raw.length && raw[raw.length - 1].trim() === "") raw.pop();
  if (!raw.length) return "";

  let contentIndent;
  if (explicitIndent) {
    contentIndent = parentIndent + Number(explicitIndent);
  } else {
    contentIndent = Infinity;
    for (const line of raw) {
      if (line.trim() !== "") contentIndent = Math.min(contentIndent, indentOf(line, cur.i));
    }
  }
  const body = raw.map((line) => (line.trim() === "" ? "" : line.slice(contentIndent)));

  let text;
  if (style === "|") {
    text = body.join("\n");
  } else {
    // Folded: blank lines become newlines, consecutive content lines join with a space.
    text = "";
    for (let idx = 0; idx < body.length; idx++) {
      if (idx === 0) text = body[idx];
      else if (body[idx] === "" || body[idx - 1] === "") text += "\n" + body[idx];
      else text += " " + body[idx];
    }
  }
  if (chomp === "-") return text;
  return text + "\n";
}

/** Split `key: value` at the first structural colon, or return null. */
function splitKey(content, lineNo) {
  let quote = null;
  for (let i = 0; i < content.length; i++) {
    const ch = content[i];
    if (quote) {
      if (ch === quote) quote = null;
      continue;
    }
    if (ch === '"' || ch === "'") {
      quote = ch;
      continue;
    }
    if (ch === "#" && i > 0 && content[i - 1] === " ") return null;
    if (ch === ":" && (i + 1 === content.length || content[i + 1] === " ")) {
      const key = content.slice(0, i).trim();
      if (!key) return null;
      if (key.startsWith("<<")) throw new YamlError("merge keys are not supported", lineNo);
      return { key: unquote(key, lineNo), rest: content.slice(i + 1).trim() };
    }
  }
  return null;
}

function stripComment(value) {
  let quote = null;
  for (let i = 0; i < value.length; i++) {
    const ch = value[i];
    if (quote) {
      if (ch === quote) quote = null;
      continue;
    }
    if (ch === '"' || ch === "'") quote = ch;
    else if (ch === "#" && (i === 0 || value[i - 1] === " ")) return value.slice(0, i).trim();
  }
  return value.trim();
}

export function parseScalar(raw, lineNo) {
  const value = stripComment(raw);
  if (value === "") return null;

  if (value[0] === "&" || value[0] === "*") {
    throw new YamlError("anchors and aliases are not supported", lineNo);
  }
  if (value[0] === "!") throw new YamlError("explicit tags are not supported", lineNo);

  if (value[0] === "[" && value[value.length - 1] === "]") {
    return splitFlow(value.slice(1, -1), lineNo).map((item) => parseScalar(item, lineNo));
  }
  if (value[0] === "{" && value[value.length - 1] === "}") {
    const map = {};
    for (const entry of splitFlow(value.slice(1, -1), lineNo)) {
      const split = splitKey(entry, lineNo);
      if (!split) throw new YamlError(`expected 'key: value' in flow mapping: ${entry}`, lineNo);
      map[split.key] = parseScalar(split.rest, lineNo);
    }
    return map;
  }
  if (value[0] === '"' || value[0] === "'") return unquote(value, lineNo);

  const lower = value.toLowerCase();
  if (lower === "true" || lower === "yes" || lower === "on") return true;
  if (lower === "false" || lower === "no" || lower === "off") return false;
  if (lower === "null" || value === "~") return null;
  if (/^[-+]?\d+$/.test(value)) return Number(value);
  if (/^[-+]?(\d+\.\d*|\.\d+)([eE][-+]?\d+)?$/.test(value)) return Number(value);
  return value;
}

function splitFlow(inner, lineNo) {
  const parts = [];
  let depth = 0;
  let quote = null;
  let start = 0;
  for (let i = 0; i < inner.length; i++) {
    const ch = inner[i];
    if (quote) {
      if (ch === quote) quote = null;
      continue;
    }
    if (ch === '"' || ch === "'") quote = ch;
    else if (ch === "[" || ch === "{") depth++;
    else if (ch === "]" || ch === "}") depth--;
    else if (ch === "," && depth === 0) {
      parts.push(inner.slice(start, i).trim());
      start = i + 1;
    }
  }
  if (depth !== 0) throw new YamlError("unbalanced flow collection", lineNo);
  const tail = inner.slice(start).trim();
  if (tail !== "") parts.push(tail);
  return parts.filter((part) => part !== "" || parts.length === 0);
}

function unquote(value, lineNo) {
  if (value.length >= 2 && value[0] === '"' && value[value.length - 1] === '"') {
    return value
      .slice(1, -1)
      .replace(/\\(["\\/nrt])/g, (_, ch) =>
        ({ n: "\n", r: "\r", t: "\t" })[ch] ?? ch,
      );
  }
  if (value.length >= 2 && value[0] === "'" && value[value.length - 1] === "'") {
    return value.slice(1, -1).replace(/''/g, "'");
  }
  if (value[0] === '"' || value[0] === "'") throw new YamlError("unterminated quoted string", lineNo);
  return value;
}
