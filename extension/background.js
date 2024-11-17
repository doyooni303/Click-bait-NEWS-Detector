// Basic setup to ensure the service worker is active
chrome.runtime.onInstalled.addListener(() => {
    console.log('Extension installed');
});

// Listen for messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Message received:', request);
    return true;
});

// Handle tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        console.log('Tab updated:', tab.url);
    }
});

// Keep service worker active
chrome.runtime.onConnect.addListener(function(port) {
    port.onDisconnect.addListener(function() {
        console.log('Port disconnected');
    });
});