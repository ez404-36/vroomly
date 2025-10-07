import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import pluginReact from "eslint-plugin-react";
import { defineConfig } from "eslint/config";

export default defineConfig([
  { files: ["**/*.{js,mjs,cjs,ts,mts,cts,jsx,tsx}"], 
    plugins: { js }, 
    extends: ["js/recommended"],
    rules: {
      "no-console": 'warn',
      "eqeqeq": 'warn',
      "curly": 'warn',
      "no-else-return": 'warn',
      "react/react-in-jsx-scope": "off",
       "react/jsx-uses-react": "off",
    },
    languageOptions: { globals: globals.browser } },
  tseslint.configs.recommended,
  pluginReact.configs.flat.recommended,
]);
