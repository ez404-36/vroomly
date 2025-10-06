import { defineConfig, globalIgnores } from "eslint/config";

export default defineConfig([
  // Игнорируем сборку
  globalIgnores(["dist", "node_modules"]),

  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      parser: "@typescript-eslint/parser",
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        window: true,
        document: true,
      },
    },
    plugins: {
      "@typescript-eslint": "@typescript-eslint/eslint-plugin",
      react: "eslint-plugin-react",
      "react-hooks": "eslint-plugin-react-hooks",
    },
    settings: {
      react: {
        version: "detect",
      },
    },
    extends: [
      "eslint:recommended",
      "plugin:@typescript-eslint/recommended",
      "plugin:react/recommended",
      "plugin:react-hooks/recommended",
      "prettier",
    ],
    rules: {
      "react/react-in-jsx-scope": "off",
      "@typescript-eslint/no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
      "react/prop-types": "off",
    },
  },
]);
