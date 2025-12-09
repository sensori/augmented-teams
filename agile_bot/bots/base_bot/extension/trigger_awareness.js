const vscode = require("vscode");
const cp = require("child_process");
const path = require("path");
const fs = require("fs");

let isActivated = false;
let extensionContext = null;
let mainCommandRegistered = false;

function registerCommands(context) {
  // Register command to check extension status
  const statusDisposable = vscode.commands.registerCommand(
    "trigger-awareness.checkStatus",
    () => {
      const status = isActivated
        ? "Extension is LOADED and ACTIVE"
        : "Extension is NOT loaded";
      vscode.window.showInformationMessage(status);
      console.log(`[Trigger Awareness] ${status}`);
      return isActivated;
    }
  );
  context.subscriptions.push(statusDisposable);

  // Register command to manually activate extension
  const activateDisposable = vscode.commands.registerCommand(
    "trigger-awareness.activate",
    () => {
      if (isActivated) {
        vscode.window.showInformationMessage(
          "Trigger Awareness Extension is already active"
        );
        console.log("[Trigger Awareness] Already activated");
        return;
      }
      // Re-run activation logic
      if (extensionContext) {
        registerMainCommand(extensionContext);
        isActivated = true;
        vscode.window.showInformationMessage(
          "Trigger Awareness Extension Manually Activated"
        );
        console.log("[Trigger Awareness] Manually activated");
      } else {
        vscode.window.showErrorMessage(
          "Cannot activate: Extension context not available. Please reload window."
        );
      }
    }
  );
  context.subscriptions.push(activateDisposable);

  // Register command to reload extension (reloads entire window)
  const reloadDisposable = vscode.commands.registerCommand(
    "trigger-awareness.reload",
    () => {
      vscode.window.showInformationMessage(
        "Reloading window to reload Trigger Awareness Extension..."
      );
      vscode.commands.executeCommand("workbench.action.reloadWindow");
    }
  );
  context.subscriptions.push(reloadDisposable);
}

function registerMainCommand(context) {
  // Prevent duplicate registration
  if (mainCommandRegistered) {
    console.log("[Trigger Awareness] Main command already registered");
    return;
  }

  const disposable = vscode.commands.registerCommand(
    "cursor.onUserMessage",
    async (message) => {
      if (!message) return;

      const workspaceRoot =
        vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || process.cwd();

      const routerScript = path.join(
        workspaceRoot,
        "agile_bot",
        "bots",
        "base_bot",
        "src",
        "cli",
        "trigger_router_entry.py"
      );

      // First: ask TriggerRouter (Python) to resolve the route
      cp.execFile(
        "python",
        [routerScript, message],
        { cwd: workspaceRoot },
        (err, stdout, stderr) => {
          if (err) {
            console.error("TriggerRouter error:", err, stderr);
            vscode.commands.executeCommand("cursor.forwardMessage", message);
            return;
          }

          let route = {};
          try {
            route = JSON.parse(stdout || "{}");
          } catch (parseErr) {
            console.error("Route parse error:", parseErr, stdout);
          }

          if (!route.bot_name) {
            vscode.commands.executeCommand("cursor.forwardMessage", message);
            return;
          }

          const cliPath = path.join(
            workspaceRoot,
            "agile_bot",
            "bots",
            route.bot_name,
            "src",
            `${route.bot_name}_cli.py`
          );

          const cliArgs = [cliPath];
          if (route.behavior_name) cliArgs.push(route.behavior_name);
          if (route.action_name) cliArgs.push(route.action_name);
          cliArgs.push("--context", message);

          // Then: run the bot CLI with resolved behavior/action
          cp.execFile(
            "python",
            cliArgs,
            { cwd: workspaceRoot },
            (cliErr, cliStdout, cliStderr) => {
              if (cliErr) {
                console.error("Bot CLI error:", cliErr, cliStderr);
              } else if (cliStdout) {
                console.log("Bot CLI output:", cliStdout);
              }
              // Always forward after handling
              vscode.commands.executeCommand("cursor.forwardMessage", message);
            }
          );
        }
      );
    }
  );

  context.subscriptions.push(disposable);
  mainCommandRegistered = true;
}

function activate(context) {
  try {
    console.log("[Trigger Awareness] Activate function called");
    extensionContext = context;
    isActivated = true;
    console.log("Trigger Awareness Extension Activated");
    vscode.window.showInformationMessage("Trigger Awareness Extension Loaded");

    // Write activation status to a file for easy checking
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || process.cwd();
    const statusFile = path.join(workspaceRoot, ".trigger-awareness-status.txt");
    try {
      fs.writeFileSync(statusFile, `Extension Activated: ${new Date().toISOString()}\n`, "utf8");
      console.log(`[Trigger Awareness] Status file written to: ${statusFile}`);
    } catch (err) {
      console.error("Could not write status file:", err);
    }

    // Register all commands
    registerCommands(context);
    registerMainCommand(context);
    console.log("[Trigger Awareness] All commands registered");
  } catch (error) {
    console.error("[Trigger Awareness] Activation error:", error);
    vscode.window.showErrorMessage(`Trigger Awareness Extension Error: ${error.message}`);
  }
}

function deactivate() {
  isActivated = false;
  extensionContext = null;
  mainCommandRegistered = false;
  console.log("Trigger Awareness Extension Deactivated");
}

module.exports = { activate, deactivate };

