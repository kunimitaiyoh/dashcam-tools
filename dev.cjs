#!/usr/bin/env node

const path = require("node:path");

process.env.TSX_TSCONFIG_PATH = path.join(__dirname, "tsconfig.json");
require("tsx/cjs/api").register();
require("./src/index.ts");
