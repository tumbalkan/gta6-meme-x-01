import { copyFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

// Entry point for the gta6-meme-x-01 bounty. The entry is an X post, and
// POST.json at the repository root names it. This program only copies that
// file to the output directory, so the house can read the post's address.
// No network, no wall clock, no other behaviour.
const botDir = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const source = join(botDir, "POST.json");
const target = join(outDir, "POST.json");
mkdirSync(outDir, { recursive: true });
copyFileSync(source, target);
