import { createRequire } from "module";
import { defineConfig } from "eslint/config";

const require = createRequire(import.meta.url);

const tsPlugin = require("@typescript-eslint/eslint-plugin");
const reactPlugin = require("eslint-plugin-react");

export default defineConfig({
  ignores: ["docs/**", ".venv/**", "docs/_static/**", "docs/_build/**"],
  languageOptions: {
    parser: require("@typescript-eslint/parser"),
    parserOptions: {
      ecmaVersion: 2020,
      sourceType: "module",
      ecmaFeatures: { jsx: true },
    },
  },
  plugins: {
    "@typescript-eslint": tsPlugin,
    react: reactPlugin,
  },
  settings: {
    react: { version: "detect" },
  },
  rules: {
    "react/react-in-jsx-scope": "off",
  },
});
