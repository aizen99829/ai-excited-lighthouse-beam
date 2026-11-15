// Riding the Lighthouse Beam — make.fun ai-excited-01 entrypoint.
//
// Node 22, standard library only. The entry image is committed beside this
// file as entry.png (rendered deterministically by render.py); this program
// only copies it to the output directory, so both grader runs produce
// byte-identical output. It never renders at grade time.
//
// Run locally with:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFile, mkdir, readFile, stat } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const target = join(outputDir, "entry.png");

await mkdir(outputDir, { recursive: true });
await copyFile(source, target);

// Verify the copy is whole: same size as the source and a real PNG.
const [srcStat, dstStat] = await Promise.all([stat(source), stat(target)]);
if (srcStat.size !== dstStat.size) {
  throw new Error(`entry.png copy truncated: ${dstStat.size} of ${srcStat.size} bytes`);
}
const magic = await readFile(target, { encoding: null }).then((b) => b.subarray(0, 8));
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!magic.equals(PNG_MAGIC)) {
  throw new Error("entry.png is not a PNG file");
}
console.log(`entry.png -> ${target} (${dstStat.size} bytes)`);
