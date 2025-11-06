export default {
  testMatch: [
    '**/?(*.)+(spec|test).[jt]s?(x)',
    '**/?(*.)+(spec|test).mjs'
  ],
  transform: {},
  testEnvironment: 'node',
  setupFiles: ['<rootDir>/jest.setup.mjs'],
};

