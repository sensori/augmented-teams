// Mock Foundry VTT globals before any imports
const hookCalls = [];
global.Hooks = { 
  on: (event, handler) => {
    hookCalls.push({ event, handler });
  }, 
  once: (event, handler) => {
    hookCalls.push({ event, handler });
  },
  _calls: hookCalls
};

global.game = { 
  settings: { 
    register: () => {}, 
    get: (module, setting) => {
      // Mock AutoRec settings to return empty arrays
      if (module === 'autoanimations') return [];
      return true;
    }
  },
  macros: {
    get: () => null,
    find: () => null
  },
  actors: {},
  user: { isGM: true }
};

global.canvas = {
  tokens: {
    get: () => null,
    controlled: [],
    placeables: []
  },
  scene: {
    dimensions: {
      width: 4000,
      height: 3000
    }
  },
  app: {
    view: {
      0: { clientWidth: 1920, clientHeight: 1080 },
      clientWidth: 1920,
      clientHeight: 1080
    }
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

// Mock Sequencer.SectionManager for DescriptorSequence
global.Sequencer.SectionManager = {
  externalSections: {
    fireEffect: { name: 'Fire' },
    iceEffect: { name: 'Ice' },
    electricityEffect: { name: 'Electricity' }
  }
};

// Mock Foundry Dialog for SequenceRunnerEditor
global.Dialog = class MockDialog {
  constructor(config) {
    Object.assign(this, config);
    return this; // SequenceRunnerEditor returns the dialog
  }
  render() { return this; }
  close() { return this; }
};

