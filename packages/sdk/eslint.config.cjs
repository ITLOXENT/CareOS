const js = require("@eslint/js");
const tseslint = require("typescript-eslint");

module.exports = [
  {
    ignores: ["dist/**", "node_modules/**", "*.cjs"],
  },

  js.configs.recommended,

  ...tseslint.configs.recommended,

  {
    files: ["src/**/*.{ts,tsx}"],
    languageOptions: {
      parserOptions: {
        project: ["./tsconfig.json"],
        tsconfigRootDir: __dirname,
      },
    },
  },
];
