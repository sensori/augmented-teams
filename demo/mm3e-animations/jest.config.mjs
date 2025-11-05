export default {
  rootDir: ".",
  testMatch: [
    "**/*.test.mjs",
    "**/*.spec.mjs"
  ],
  testPathIgnorePatterns: [
    "/node_modules/"
  ],
  moduleFileExtensions: [
    "mjs",
    "js"
  ],
  transform: {},
  testEnvironment: "node",
  moduleNameMapper: {
    "^(\\.{1,2}/.*)\\.js$": "$1"
  },
  watchman: false
};

