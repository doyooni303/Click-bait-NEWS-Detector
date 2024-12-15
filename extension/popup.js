document.addEventListener('DOMContentLoaded', function() {
  const startButton = document.getElementById('startButton');
  const cancelButton = document.getElementById('cancelButton');
  const stopButton = document.getElementById('stopButton');
  const progressContainer = document.getElementById('progressContainer');
  const progressBar = document.getElementById('progressBar');
  const progressText = document.getElementById('progressText');
  const currentTitle = document.getElementById('currentTitle');
  
  let port = chrome.runtime.connect({ name: 'popup' });

  // Check state when popup opens
  chrome.runtime.sendMessage({ type: 'getState' }, (state) => {
    if (state && state.isAnalyzing) {
      startButton.style.display = 'none';
      cancelButton.style.display = 'none';
      stopButton.style.display = 'block';
      progressContainer.style.display = 'block';
      progressBar.style.width = `${state.progress}%`;
      progressText.textContent = `${state.progress}%`;
    } else {
      // Initial state
      startButton.style.display = 'block';
      cancelButton.style.display = 'block';
      stopButton.style.display = 'none';
      progressContainer.style.display = 'none';
    }
  });

  startButton.addEventListener('click', async () => {
    // Set analyzing state
    chrome.runtime.sendMessage({ 
      type: 'setState', 
      state: { isAnalyzing: true, progress: 0 }
    });

    startButton.style.display = 'none';
    cancelButton.style.display = 'none';
    stopButton.style.display = 'block';
    progressContainer.style.display = 'block';
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
    
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    chrome.tabs.sendMessage(tab.id, { action: 'startAnalysis' });
  });

  cancelButton.addEventListener('click', async () => {
    // Just close the popup for cancel
    window.close();
  });

  stopButton.addEventListener('click', async () => {
    // Reset analyzing state
    chrome.runtime.sendMessage({ 
      type: 'setState', 
      state: { isAnalyzing: false }
    });

    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    chrome.tabs.sendMessage(tab.id, { action: 'stopAnalysis' });
    
    startButton.style.display = 'block';
    cancelButton.style.display = 'block';
    stopButton.style.display = 'none';
    progressContainer.style.display = 'none';
  });

  // Listen for messages from background script
  port.onMessage.addListener((message) => {
    if (message.type === 'progress') {
      // Ensure progress container is visible
      progressContainer.style.display = 'block';
      
      // Update progress bar
      const progressValue = Math.min(Math.round(message.progress), 100);
      progressBar.style.width = `${progressValue}%`;
      progressText.textContent = `${progressValue}%`;
      
      // Update UI based on progress
      if (progressValue === 100) {
        setTimeout(() => {
          chrome.runtime.sendMessage({ 
            type: 'setState', 
            state: { isAnalyzing: false }
          });
          startButton.style.display = 'block';
          cancelButton.style.display = 'block';
          stopButton.style.display = 'none';
          progressContainer.style.display = 'none';
          currentTitle.textContent = '';
        }, 1000); // Give time to see 100%
      }
    } else if (message.type === 'processing') {
      currentTitle.textContent = message.title;
    }
  });
});