module.exports = {
  root: true,
  env: {
    node: true,
    jquery: true,
  },
  extends: ["plugin:vue/essential", "@vue/standard", "@vue/typescript"],
  rules: {
    "no-console": process.env.NODE_ENV === "production" ? "error" : "off",
    "no-debugger": process.env.NODE_ENV === "production" ? "error" : "off",

    // allow semicolons
    semi: 0,
    // string's ...
    // "quotes": [1, 'backtick', 'single'],
    quotes: 0,
    // allow async-await
    "generator-star-spacing": "off",

    "padded-blocks": "off",

    // TEMPORARIAMENTE .. por causa do vuex e das que vêm do servidor
    camelcase: 0,

    "no-multiple-empty-lines": 0,

    "object-shorthand": "off",

    "no-unused-vars": "off",
    // // TEMPORARIAMENTE ... senão com a passagem para TS ... era o caos
    "@typescript-eslint/no-unused-vars": "off",
    // ["error", {
    //   "vars": "all",
    //   "args": "off", // "after-used",
    //   "ignoreRestSiblings": false
    // }]
    "space-before-function-paren": 1,
    "no-trailing-spaces": 1,
    "no-multi-spaces": 1,
    indent: ["error", 2],
    "no-tabs": 1,
    "no-mixed-spaces-and-tabs": 1,
    "comma-dangle": ["error", "always-multiline"],
    "computed-property-spacing": ["error", "never"],
  },
  parserOptions: {
    parser: "@typescript-eslint/parser",
  },
  globals: {
    kendo: false,
  },
};
