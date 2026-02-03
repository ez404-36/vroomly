/** @type {import('stylelint').Config} */
export default {
  extends: ['stylelint-config-standard'],
  plugins: ['@stylistic/stylelint-plugin'],
  rules: {
    /* 🔠 Форматирование */
    '@stylistic/indentation': 2, // отступы в 2 пробела
    '@stylistic/number-leading-zero': 'always', // 0 перед десятичной частью (0.5, не .5)
    '@stylistic/string-quotes': 'single', // одинарные кавычки
    '@stylistic/max-empty-lines': 1, // максимум одна пустая строка подряд
    '@stylistic/no-eol-whitespace': true, // без пробелов в конце строки
    '@stylistic/color-hex-case': 'lower', // цвета в нижнем регистре

    /* 🎨 Цвета и значения */
    'color-named': 'never', // не использовать имена цветов (только HEX, RGB, HSL)
    'font-weight-notation': 'numeric', // числовые значения для font-weight

    /* 📐 Селекторы */
    'selector-class-pattern': '^[a-z0-9\\-]+$', // классы в kebab-case

    /* 🔁 Свойства */
    'declaration-block-no-duplicate-properties': true, // не дублировать свойства
    '@stylistic/declaration-block-trailing-semicolon': 'always', // ставить ; после последнего свойства
    'declaration-block-single-line-max-declarations': 1, // каждое свойство — на новой строке
    '@stylistic/declaration-colon-space-after': 'always-single-line', // пробел после :
    '@stylistic/declaration-colon-space-before': 'never', // без пробела перед :

    /* 📦 Блоки */
    '@stylistic/block-opening-brace-space-before': 'always', // пробел перед {
    '@stylistic/block-closing-brace-newline-after': 'always', // новая строка после }

    /* 🚫 Ошибки и предупреждения */
    'no-duplicate-selectors': true, // запрет на одинаковые селекторы
    'property-no-unknown': [
      true,
      {
        ignoreProperties: ['composes'], // нужно для CSS Modules (composes: button;)
      },
    ],
    'unit-no-unknown': true, // запрет неизвестных единиц измерения
  },
  ignoreFiles: ['**/node_modules/**', '**/dist/**', '**/build/**'],
};
