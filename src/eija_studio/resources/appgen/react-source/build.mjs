// Maintainer build only. Generated Python apps run the committed bundle without Node.
import {build} from "esbuild";
import {readFile, writeFile, mkdir} from "node:fs/promises";
import {fileURLToPath} from "node:url";
import {dirname, resolve} from "node:path";
import {createHash} from "node:crypto";

const source = dirname(fileURLToPath(import.meta.url));
const out = resolve(source, process.env.EIJA_REACT_OUTPUT || "../app/web");
const sha256 = value => createHash("sha256").update(value).digest("hex");
const authored = ["main.jsx", "controller.js", "app.css", "package.json", "package-lock.json", "build.mjs", "LICENSES.txt"];
const result = await build({entryPoints: [resolve(source, "main.jsx")], bundle: true, write: false,
  format: "iife", target: ["es2020"], minify: true, legalComments: "inline", charset: "utf8",
  define: {"process.env.NODE_ENV": '"production"'}, logLevel: "warning"});
const controller = await readFile(resolve(source, "controller.js"), "utf8");
const outputs = {"app.js": `${controller}\n${result.outputFiles[0].text}`, "app.css": await readFile(resolve(source, "app.css"), "utf8")};
const packageInfo = JSON.parse(await readFile(resolve(source, "package.json"), "utf8"));
const sources = Object.fromEntries(await Promise.all(authored.map(async name => [name, sha256(await readFile(resolve(source, name)))])));
const manifest = {format: "eija.react-frontend.v1", tool: {name: "esbuild", version: packageInfo.devDependencies.esbuild},
  dependencies: packageInfo.dependencies, sources, outputs: Object.fromEntries(Object.entries(outputs).map(([name, value]) => [name, sha256(value)])),
  runtime: {node_required: false, network_required: false, csp: "external scripts and styles; no unsafe-inline or unsafe-eval"}};
const manifestText = JSON.stringify(manifest, null, 2) + "\n";
if (process.argv.includes("--check")) {
  for (const [name, content] of Object.entries(outputs)) if (await readFile(resolve(out, name), "utf8") !== content) throw new Error(`${name} differs from the pinned authored source`);
  if (await readFile(resolve(source, "build-manifest.json"), "utf8") !== manifestText) throw new Error("Frontend build manifest is stale");
  console.log("PASS: pinned React source reproduces the committed JavaScript, CSS and build manifest");
} else {
  await mkdir(out, {recursive: true});
  for (const [name, content] of Object.entries(outputs)) await writeFile(resolve(out, name), content, "utf8");
  await writeFile(resolve(source, "build-manifest.json"), manifestText, "utf8");
  console.log(`Built ${Object.keys(outputs).join(", ")} from pinned React source`);
}
