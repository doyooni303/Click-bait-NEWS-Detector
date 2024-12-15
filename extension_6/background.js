let ports = new Set();
let analysisState = {
  isAnalyzing: false,
  progress: 0
};

// Handle popup connections
chrome.runtime.onConnect.addListener((port) => {
  if (port.name === 'popup') {
    ports.add(port);
    port.onDisconnect.addListener(() => {
      ports.delete(port);
    });
  }
});

// Handle messages
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'getState') {
    sendResponse(analysisState);
  } else if (message.type === 'setState') {
    analysisState = { ...analysisState, ...message.state };
  } else if (message.type === 'progress') {
    analysisState.progress = message.progress;
    // Forward progress to all connected popups
    ports.forEach(port => {
      port.postMessage(message);
    });
  } else if (message.type === 'error' || message.type === 'stopped') {
    analysisState.isAnalyzing = false;
    // Forward error/stopped status to all connected popups
    ports.forEach(port => {
      port.postMessage(message);
    });
  }
  return true;
});