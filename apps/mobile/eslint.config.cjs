const js = require("@eslint/js");
const tseslint = require("typescript-eslint");

module.exports = [
  {
    ignores: [
      "node_modules/**",
      "dist/**",
      "build/**",
      "coverage/**",
      "android/**",
      "ios/**",
      "*.config.js",
      "*.config.cjs",
      "*.config.mjs",
      "babel.config.js",
      "metro.config.js",
      "jest.config.*",
      "eslint.config.*",
    ],
  },

  {
    files: ["**/*.{js,jsx}"],
    ...js.configs.recommended,
  },

  ...tseslint.configs.recommended,

  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      parserOptions: {
        project: ["./tsconfig.json"],
        tsconfigRootDir: __dirname,
      },
    },
  },
];
