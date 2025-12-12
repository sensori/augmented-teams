const vscode = require("vscode");
const cp = require("child_process");
const path = require("path");
const fs = require("fs");

let outputChannel = null;

function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}`;
  console.log(logMessage);
  if (outputChannel) {
    outputChannel.appendLine(logMessage);
  }
}

// Get list of all available bots from registry
function getAvailableBots(workspaceRoot) {
  const registryPath = path.join(workspaceRoot, "agile_bot", "bots", "registry.json");
  try {
    const registryContent = fs.readFileSync(registryPath, "utf8");
    const registry = JSON.parse(registryContent);
    return registry;
  } catch (err) {
    log(`ERROR: Could not read bot registry: ${err.message}`);
    return {};
  }
}

// Get story_bot behaviors and actions by calling CLI --list
function getStoryBotCommands(workspaceRoot) {
  const cliPath = path.join(workspaceRoot, "agile_bot", "bots", "story_bot", "src", "story_bot_cli.py");
  
  return new Promise((resolve) => {
    cp.execFile("python", [cliPath, "--list"], { cwd: workspaceRoot }, (err, stdout, stderr) => {
      if (err) {
        log(`ERROR: Could not get story_bot commands: ${err.message}`);
        resolve({});
        return;
      }
      
      try {
        const result = JSON.parse(stdout);
        resolve(result);
      } catch (parseErr) {
        log(`ERROR: Could not parse story_bot commands: ${parseErr.message}`);
        resolve({});
      }
    });
  });
}

// Get current workflow state
function getCurrentWorkflowState(workspaceRoot) {
  const statePath = path.join(workspaceRoot, "agile_bot", "bots", "story_bot", "workflow_state.json");
  try {
    const stateContent = fs.readFileSync(statePath, "utf8");
    const state = JSON.parse(stateContent);
    return state;
  } catch (err) {
    log(`INFO: No workflow state found (${err.message})`);
    return null;
  }
}

// Load trigger words for a specific behavior
function getBehaviorTriggerWords(workspaceRoot, behaviorName) {
  // Try behavior.json first (new format)
  const behaviorPath = path.join(
    workspaceRoot, 
    "agile_bot", 
    "bots", 
    "story_bot", 
    "behaviors", 
    behaviorName, 
    "behavior.json"
  );
  
  try {
    const content = fs.readFileSync(behaviorPath, "utf8");
    const behaviorData = JSON.parse(content);
    const triggerWords = behaviorData.trigger_words || {};
    if (triggerWords.patterns && triggerWords.patterns.length > 0) {
      return triggerWords.patterns;
    }
  } catch (err) {
    // Fall through to old format
  }
  
  // Fallback to old format for backward compatibility
  const triggerPath = path.join(
    workspaceRoot, 
    "agile_bot", 
    "bots", 
    "story_bot", 
    "behaviors", 
    behaviorName, 
    "trigger_words.json"
  );
  
  try {
    const content = fs.readFileSync(triggerPath, "utf8");
    const triggers = JSON.parse(content);
    return triggers.patterns || [];
  } catch (err) {
    log(`INFO: No trigger words for ${behaviorName}: ${err.message}`);
    return [];
  }
}

// Check if message contains help-related keywords
function isHelpRequest(message) {
  const helpKeywords = [
    "help",
    "what can i do",
    "what can you do",
    "how do i",
    "get started",
    "getting started",
    "not sure how",
    "don't know how",
    "show me",
    "available"
  ];
  
  const lowerMessage = message.toLowerCase();
  return helpKeywords.some(keyword => lowerMessage.includes(keyword));
}

// Match message against behavior trigger words
function matchBehavior(message, workspaceRoot) {
  const behaviors = [
    "1_shape",
    "2_prioritization", 
    "4_discovery",
    "5_exploration",
    "6_scenarios",
    "7_tests",
    "8_code"
  ];
  
  for (const behavior of behaviors) {
    const triggers = getBehaviorTriggerWords(workspaceRoot, behavior);
    const lowerMessage = message.toLowerCase();
    
    for (const trigger of triggers) {
      // Convert trigger pattern to regex
      const pattern = new RegExp(trigger, "i");
      if (pattern.test(lowerMessage)) {
        return behavior.substring(2); // Remove number prefix
      }
    }
  }
  
  return null;
}

// Register @agilebot chat participant
function registerAgileBotParticipant(context, workspaceRoot) {
  const handler = async (request, chatContext, stream, token) => {
    log(`@agilebot received: "${request.prompt}"`);
    
    const registry = getAvailableBots(workspaceRoot);
    
    stream.markdown(`## Available Agile Bots\n\n`);
    
    for (const [botName, botInfo] of Object.entries(registry)) {
      stream.markdown(`### @${botName}\n`);
      if (botInfo.description) {
        stream.markdown(`${botInfo.description}\n\n`);
      }
      stream.markdown(`Use \`@${botName} help\` for more information\n\n`);
    }
    
    return {};
  };
  
  const participant = vscode.chat.createChatParticipant("chat-participants.agilebot", handler);
  context.subscriptions.push(participant);
  log("@agilebot participant registered");
}

// Register @storybot chat participant
function registerStoryBotParticipant(context, workspaceRoot) {
  const handler = async (request, chatContext, stream, token) => {
    log(`@storybot received: "${request.prompt}"`);
    
    const message = request.prompt.trim();
    
    // Pattern 1: Help request
    if (isHelpRequest(message)) {
      log("Detected help request");
      
      const commands = await getStoryBotCommands(workspaceRoot);
      
      stream.markdown(`## Story Bot - Behaviors and Actions\n\n`);
      
      if (commands.behaviors) {
        for (const [behaviorName, behaviorInfo] of Object.entries(commands.behaviors)) {
          stream.markdown(`### ${behaviorName}\n`);
          if (behaviorInfo.description) {
            stream.markdown(`*${behaviorInfo.description}*\n\n`);
          }
          if (behaviorInfo.actions) {
            stream.markdown(`**Actions:**\n`);
            for (const actionName of behaviorInfo.actions) {
              stream.markdown(`- ${actionName}\n`);
            }
            stream.markdown(`\n`);
          }
        }
      }
      
      stream.markdown(`\n---\n\n`);
      stream.markdown(`**Usage:**\n`);
      stream.markdown(`- \`@storybot <behavior-keyword>\` - Start a specific behavior\n`);
      stream.markdown(`- \`@storybot\` (no parameters) - Continue from current state\n\n`);
      
      return {};
    }
    
    // Pattern 2: Behavior-specific trigger words (no message = Pattern 3)
    let targetBehavior = null;
    let targetAction = null;
    
    if (message.length > 0) {
      targetBehavior = matchBehavior(message, workspaceRoot);
      log(`Matched behavior: ${targetBehavior}`);
    }
    
    // Pattern 3: No parameters - use current workflow state (or first behavior if no state)
    if (!targetBehavior && message.length === 0) {
      log("No parameters provided, will use bot's default routing (workflow state or first behavior)");
      // Set a flag to indicate we're using default routing
      targetBehavior = "__default__";
      targetAction = "__default__";
    }
    
    // If we have a target behavior, show command and ask for confirmation
    if (targetBehavior) {
      // Show the CLI command that will be executed
      stream.markdown(`**CLI Command to execute:**\n\n`);
      
      if (targetBehavior === "__default__") {
        stream.markdown(`\`\`\`bash\npython agile_bot/bots/story_bot/src/story_bot_cli.py\n\`\`\`\n\n`);
        stream.markdown(`This will continue from current workflow state (or start at the beginning).\n\n`);
      } else {
        let cliCommand = `python agile_bot/bots/story_bot/src/story_bot_cli.py ${targetBehavior}`;
        if (targetAction) {
          cliCommand += ` ${targetAction}`;
        }
        stream.markdown(`\`\`\`bash\n${cliCommand}\n\`\`\`\n\n`);
        const actionText = targetAction ? ` → **${targetAction}**` : "";
        stream.markdown(`This will run **story_bot** → **${targetBehavior}**${actionText}\n\n`);
      }
      
      // Now ask for confirmation
      stream.markdown(`---\n\n`);
      stream.markdown(`Do you want to execute this? *(respond without @bot prefix please)*\n\n`);
      
      return {};
    }
    
    // No match found
    stream.markdown(`I couldn't determine what you'd like to do. Try:\n\n`);
    stream.markdown(`- \`@storybot help\` - See all available behaviors and actions\n`);
    stream.markdown(`- \`@storybot <behavior-keyword>\` - Start a specific behavior\n`);
    stream.markdown(`- \`@storybot\` (no text) - Continue from where you left off\n\n`);
    
    return {};
  };
  
  const participant = vscode.chat.createChatParticipant("chat-participants.storybot", handler);
  context.subscriptions.push(participant);
  log("@storybot participant registered");
}

function activate(context) {
  try {
    outputChannel = vscode.window.createOutputChannel("Agile Chat Participants");
    outputChannel.show(true);
    
    log("Activating Agile Chat Participants");
    
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || process.cwd();
    
    // Register both chat participants
    registerAgileBotParticipant(context, workspaceRoot);
    registerStoryBotParticipant(context, workspaceRoot);
    
    log("All chat participants registered successfully");
    vscode.window.showInformationMessage("Agile Chat Participants Loaded");
  } catch (error) {
    log(`ERROR: Activation failed: ${error.message}`);
    vscode.window.showErrorMessage(`Chat Participants Error: ${error.message}`);
  }
}

function deactivate() {
  log("Deactivating Agile Chat Participants");
  if (outputChannel) {
    outputChannel.dispose();
    outputChannel = null;
  }
}

module.exports = { activate, deactivate };
