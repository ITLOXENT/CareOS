const next = require("@next/eslint-plugin-next");
const tseslint = require("typescript-eslint");

module.exports = [
  {
    ignores: [".next/**", "node_modules/**", "dist/**", "build/**"],
  },
  {
    plugins: {
      "@next/next": next,
      "@typescript-eslint": tseslint.plugin,
    },
    rules: {
      ...next.configs.recommended.rules,
      ...next.configs["core-web-vitals"].rules,
      ...tseslint.configs.recommended[0].rules,
    },
  },
];
