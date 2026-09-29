import { join } from "node:path";

// src/ からも dist/ からも 1 つ上がパッケージルート。
export const packageRoot = join(__dirname, "..");
