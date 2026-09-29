import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    server: {
      deps: {
        // clipanion 3 の ESM ビルドはディレクトリ import（"../platform"）を含み Node では読めないため、Vite に変換させる。
        inline: ["clipanion"],
      },
    },
  },
});
