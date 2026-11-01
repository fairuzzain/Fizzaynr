// Local MCP server (stdio) for Claude Desktop chat: generates images with Codex CLI
// through codex-image.ps1. No dependencies; newline-delimited JSON-RPC 2.0.
import { spawn } from "node:child_process";
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from "node:fs";
import { tmpdir, homedir } from "node:os";
import { join, dirname, isAbsolute } from "node:path";
import { fileURLToPath } from "node:url";
import { randomUUID } from "node:crypto";

const HERE = dirname(fileURLToPath(import.meta.url));
const SCRIPT = join(HERE, "codex-image.ps1");
const DEFAULT_DIR = process.env.CODEX_IMAGE_DIR || join(homedir(), "Documents", "Gambar AI");

const TOOL = {
  name: "generate_image",
  description:
    "Generate a still image with the user's OpenAI Codex CLI (their ChatGPT login) on this PC and save it as a PNG. " +
    "Use whenever the user asks for an image, poster, thumbnail, illustration, scene frame or character, and whenever a skill " +
    "asks for an image from a connector that is not available (Magnific, Higgsfield, Freepik, Midjourney, Flux, etc.) - pass that " +
    "skill's prompt and aspect ratio unchanged. RB Digital: after rb-digital-poster writes its poster prompt, offer to render it " +
    "here (ratio 4:5, width 1080); for rb-digital-video Mode B, generate each Google Flow prompt here instead of asking the user " +
    "to use Flow (2x2/4x4 sheets 1:1 width 2048, backgrounds 9:16 width 1080; pass sheet 1's path as reference_images for later " +
    "sheets); for rbdigital-parallax generate its backgrounds (9:16 width 1536) and its green/magenta character and fg sheets " +
    "(16:9 width 2560, pad=true) here; for vox-collage-explainer generate its photo/engraving/props images (16:9 width 1920) here instead of ElevenLabs images.Files are saved on the user's PC: if this chat's sandbox cannot read them, tell the user the paths to upload back. " +
    "Takes 1-3 minutes per image. Returns the saved file path and a preview. " +
    "Still images only: no video, lip-sync or upscaling.",
  inputSchema: {
    type: "object",
    properties: {
      prompt: { type: "string", description: "Full image prompt (any language). Put text that must appear in the image in quotes." },
      aspect_ratio: { type: "string", description: "Exact output ratio, e.g. 16:9, 9:16, 1:1, 4:5, 3:4, 21:9. Default 1:1." },
      width: { type: "integer", description: "Optional final width in pixels, e.g. 1920 for 16:9 or 1080 for 9:16." },
      filename: { type: "string", description: "Optional short kebab-case file name without extension. Existing files are never overwritten." },
      output_folder: { type: "string", description: `Optional absolute folder on this PC. Default: ${DEFAULT_DIR}` },
      pad: {
        type: "boolean",
        description: "Fit the whole image and pad it to aspect_ratio with its own background colour instead of cropping. Use for green/magenta key sheets (rbdigital-parallax character and fg sheets).",
      },
      reference_images: {
        type: "array",
        items: { type: "string" },
        description: "Optional absolute paths of images on this PC to use as reference (image-to-image, same character, style match, edit). Can be paths returned by earlier generate_image calls.",
      },
    },
    required: ["prompt"],
  },
};

function send(msg) {
  process.stdout.write(JSON.stringify(msg) + "\n");
}

function slug(text) {
  const s = text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 40).replace(/-+$/, "");
  const stamp = new Date().toISOString().replace(/[-:T]/g, "").slice(0, 14);
  return `${s || "image"}-${stamp}`;
}

function runScript(args, onTick) {
  return new Promise((resolve) => {
    const child = spawn("powershell.exe", ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", SCRIPT, ...args], {
      windowsHide: true,
    });
    let out = "";
    let err = "";
    child.stdout.on("data", (d) => (out += d));
    child.stderr.on("data", (d) => (err += d));
    const timer = setInterval(onTick, 10000);
    child.on("close", (code) => {
      clearInterval(timer);
      resolve({ code, out, err });
    });
  });
}

async function generate(params, progressToken) {
  const prompt = String(params.prompt || "").trim();
  if (!prompt) throw new Error("prompt is required");
  const folder = params.output_folder && isAbsolute(params.output_folder) ? params.output_folder : DEFAULT_DIR;
  mkdirSync(folder, { recursive: true });
  const name = (params.filename ? String(params.filename).replace(/\.png$/i, "").replace(/[^A-Za-z0-9._-]+/g, "-") : "") || slug(prompt);

  const work = join(tmpdir(), "codex-image-mcp", randomUUID());
  mkdirSync(work, { recursive: true });
  const promptFile = join(work, "prompt.txt");
  const previewFile = join(work, "preview.jpg");
  writeFileSync(promptFile, prompt, "utf8");

  const args = ["-PromptFile", promptFile, "-Out", join(folder, `${name}.png`), "-Preview", previewFile];
  args.push("-Aspect", String(params.aspect_ratio || "1:1"));
  if (params.width) args.push("-Width", String(parseInt(params.width, 10)));
  if (params.pad) args.push("-Pad", "auto");
  const refs = Array.isArray(params.reference_images) ? params.reference_images.filter(Boolean) : [];
  if (refs.length) args.push("-Reference", refs.join("|")); // -File can't pass arrays; '|' is never in a Windows path

  let tick = 0;
  const { code, out, err } = await runScript(args, () => {
    tick++;
    if (progressToken !== undefined) {
      send({ jsonrpc: "2.0", method: "notifications/progress", params: { progressToken, progress: tick, message: `Generating with Codex... ${tick * 10}s` } });
    }
  });

  try {
    const line = out.trim().split(/\r?\n/).filter((l) => l.trim().startsWith("{")).pop();
    if (code !== 0 || !line) {
      const msg = (err || out).split(/\r?\n/).filter((l) => l.trim() && !/rmcp::transport/.test(l)).slice(-15).join("\n");
      return { isError: true, content: [{ type: "text", text: `Image generation failed (exit ${code}).\n${msg}` }] };
    }
    const info = JSON.parse(line);
    const content = [
      { type: "text", text: `Saved PNG: ${info.Path}\nSize: ${info.Width}x${info.Height} px (${Math.round(info.Bytes / 1024)} KB). Generated by Codex CLI.` },
    ];
    if (existsSync(previewFile)) {
      content.push({ type: "image", data: readFileSync(previewFile).toString("base64"), mimeType: "image/jpeg" });
    }
    return { content };
  } finally {
    rmSync(work, { recursive: true, force: true });
  }
}

async function handle(msg) {
  const { id, method, params = {} } = msg;
  if (id === undefined) return; // notifications (initialized, cancelled, ...)
  try {
    if (method === "initialize") {
      return send({
        jsonrpc: "2.0",
        id,
        result: {
          protocolVersion: params.protocolVersion || "2025-06-18",
          capabilities: { tools: {} },
          serverInfo: { name: "codex-image", version: "1.0.0" },
        },
      });
    }
    if (method === "ping") return send({ jsonrpc: "2.0", id, result: {} });
    if (method === "tools/list") return send({ jsonrpc: "2.0", id, result: { tools: [TOOL] } });
    if (method === "tools/call") {
      if (params.name !== TOOL.name) throw new Error(`Unknown tool: ${params.name}`);
      const result = await generate(params.arguments || {}, params._meta?.progressToken);
      return send({ jsonrpc: "2.0", id, result });
    }
    send({ jsonrpc: "2.0", id, error: { code: -32601, message: `Method not found: ${method}` } });
  } catch (e) {
    send({ jsonrpc: "2.0", id, result: { isError: true, content: [{ type: "text", text: String(e?.message || e) }] } });
  }
}

let buf = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => {
  buf += chunk;
  let i;
  while ((i = buf.indexOf("\n")) >= 0) {
    const line = buf.slice(0, i).trim();
    buf = buf.slice(i + 1);
    if (!line) continue;
    let msg;
    try { msg = JSON.parse(line); } catch { continue; }
    handle(msg);
  }
});
