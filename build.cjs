const { build } = require("esbuild");
const { dependencies } = require("./package.json");

build({
  entryPoints: ["src/index.ts"],
  outfile: "dist/index.js",
  bundle: true,
  platform: "node",
  format: "cjs",
  target: "node26",
  external: Object.keys(dependencies),
  banner: { js: "#!/usr/bin/env node" },
}).catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
