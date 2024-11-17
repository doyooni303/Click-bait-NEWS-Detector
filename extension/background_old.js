// Handle installation and updates
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        // First time installation
        console.log('Extension installed successfully');
        
        // Optional: Open a welcome page
        chrome.tabs.create({
            url: 'popup/welcome.html'
        });
    } else if (details.reason === 'update') {
        // Extension updated
        console.log('Extension updated to version', chrome.runtime.getManifest().version);
    }
});


// Function to check if URL is a valid Naver news article
function isValidNewsUrl(url) {
    const validPatterns = [
        'n.news.naver.com/article/',
        'm.sports.naver.com/article/',
        'entertain.naver.com/article/'
    ];

    return validPatterns.some(pattern => url.includes(pattern));
}

// Listen for tab updates to manage the extension icon
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete') {
        // Check if the current page is a valid Naver news article
        if (tab.url && isValidNewsUrl(tab.url)) {
            // Enable the extension icon
            chrome.action.setIcon({
                tabId: tabId,
                path: {
                    "16": "icons/icon16.png",
                    "48": "icons/icon48.png",
                    "128": "icons/icon128.png"
                }
            });
            // Enable the popup
            chrome.action.setPopup({
                tabId: tabId,
                popup: "popup/popup.html"
            });
        } else {
            // Disable the extension icon (make it gray)
            chrome.action.setIcon({
                tabId: tabId,
                path: {
                    "16": "icons/icon16_disabled.png",
                    "48": "icons/icon48_disabled.png",
                    "128": "icons/icon128_disabled.png"
                }
            });
            // Set a different popup for non-news pages
            chrome.action.setPopup({
                tabId: tabId,
                popup: "popup/disabled.html"
            });
        }
    }
});

// Cache management for API responses
const cache = new Map();

// Handle messages from popup and content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    switch (request.action) {
        case 'analyze':
            // Handle analysis request
            handleAnalysis(request.url, request.category)
                .then(sendResponse)
                .catch(error => sendResponse({ error: error.message }));
            return true; // Will respond asynchronously

        case 'clearCache':
            // Clear cached results
            cache.clear();
            sendResponse({ message: 'Cache cleared' });
            break;

        case 'checkServer':
            // Check if the backend server is running
            checkServerStatus()
                .then(sendResponse)
                .catch(error => sendResponse({ error: error.message }));
            return true;
    }
});

// Function to handle article analysis
async function handleAnalysis(url, category) {
    // Check cache first
    const cacheKey = `${url}-${category}`;
    if (cache.has(cacheKey)) {
        return cache.get(cacheKey);
    }

    try {
        const response = await fetch('http://localhost:8000/BERT/detect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url, category })
        });

        if (!response.ok) {
            throw new Error('서버 응답 오류');
        }

        const result = await response.json();
        
        // Cache the result
        cache.set(cacheKey, result);
        
        // Clear old cache entries if cache is too large
        if (cache.size > 100) {
            const firstKey = cache.keys().next().value;
            cache.delete(firstKey);
        }

        return result;

    } catch (error) {
        console.error('Analysis error:', error);
        throw new Error('분석 중 오류가 발생했습니다');
    }
}

// Function to check server status
async function checkServerStatus() {
    try {
        const response = await fetch('http://localhost:8000/BERT/home', {
            method: 'GET'
        });
        
        return { 
            status: response.ok,
            message: response.ok ? 'Server is running' : 'Server is not responding'
        };
    } catch (error) {
        return { 
            status: false, 
            message: 'Server is not running'
        };
    }
}

// Optional: Performance monitoring
let analysisTimeLog = [];

function logAnalysisTime(startTime, endTime) {
    const duration = endTime - startTime;
    analysisTimeLog.push(duration);
    
    // Keep only last 50 measurements
    if (analysisTimeLog.length > 50) {
        analysisTimeLog.shift();
    }
    
    // Calculate average processing time
    const average = analysisTimeLog.reduce((a, b) => a + b, 0) / analysisTimeLog.length;
    console.log(`Average analysis time: ${average}ms`);
}

// Optional: Error reporting
function reportError(error, context) {
    console.error('Error in extension:', {
        message: error.message,
        context: context,
        timestamp: new Date().toISOString(),
        url: context.url || 'unknown'
    });
}

chrome.runtime.onInstalled.addListener(() => {
    console.log('Extension installed');
});

// Add this to your content.js for debugging
console.log('Content script loaded');

// Add this to your popup.js for debugging
document.addEventListener('DOMContentLoaded', () => {
    console.log('Popup loaded');
});