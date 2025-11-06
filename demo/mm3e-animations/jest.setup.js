// Mock Foundry VTT globals before any imports
global.Hooks = { 
  on: () => {}, 
  once: () => {} 
};

global.game = { 
  settings: { 
    register: () => {}, 
    get: () => true 
  },
  macros: {},
  actors: {},
  user: { isGM: true }
};

global.canvas = {
  tokens: {
    get: () => null,
    controlled: [],
    placeables: []
  }
};

global.ui = {
  notifications: {
    error: () => {},
    warn: () => {},
    info: () => {}
  }
};

global.Sequencer = class MockSequencer {
  constructor() {
    this.effects = [];
  }
  effect() { return this; }
  file() { return this; }
  atLocation() { return this; }
  play() { return Promise.resolve(); }
};



