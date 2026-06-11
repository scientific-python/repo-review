import { defineConfig, globalIgnores } from "eslint/config";
import tseslint from "typescript-eslint";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import prettier from "eslint-config-prettier";

export default defineConfig(
  globalIgnores([
    "docs/**",
    "dist/**",
    "out/**",
    ".venv/**",
    "node_modules/**",
  ]),
  {
    files: ["src/**/*.{ts,tsx}", "*.{js,mjs,cjs}"],
    extends: [
      tseslint.configs.recommended,
      react.configs.flat.recommended,
      react.configs.flat["jsx-runtime"],
      reactHooks.configs.flat.recommended,
      prettier,
    ],
    settings: {
      // eslint-plugin-react's "detect" mode crashes under ESLint 10
      // (it relies on the removed context.getFilename API), so pin it.
      react: { version: "19" },
    },
    rules: {
      "react/react-in-jsx-scope": "off",
      // Props are typed with TypeScript interfaces instead of PropTypes
      "react/prop-types": "off",
    },
  },
);
