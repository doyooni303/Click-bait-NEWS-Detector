document.addEventListener('DOMContentLoaded', function() {
  const startButton = document.getElementById('startButton');
  const cancelButton = document.getElementById('cancelButton');
  const progressContainer = document.getElementById('progressContainer');
  const progressBar = document.getElementById('progressBar');
  const progressText = document.getElementById('progressText');

  // Check state when popup opens
  chrome.runtime.sendMessage({ type: 'getState' }, (state) => {
    if (state.isAnalyzing) {
      startButton.style.display = 'none';
      cancelButton.style.display = 'block';
      progressContainer.style.display = 'block';
      progressBar.style.width = `${state.progress}%`;
      progressText.textContent = `${state.progress}%`;
    }
  });

  startButton.addEventListener('click', async () => {
    // Set analyzing state
    chrome.runtime.sendMessage({ 
      type: 'setState', 
      state: { isAnalyzing: true, progress: 0 }
    });

    startButton.style.display = 'none';
    cancelButton.style.display = 'block';
    progressContainer.style.display = 'block';
    
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    chrome.tabs.sendMessage(tab.id, { action: 'startAnalysis' });
  });

  cancelButton.addEventListener('click', async () => {
    // Reset analyzing state
    chrome.runtime.sendMessage({ 
      type: 'setState', 
      state: { isAnalyzing: false }
    });

    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    chrome.tabs.sendMessage(tab.id, { action: 'stopAnalysis' });
    
    startButton.style.display = 'block';
    cancelButton.style.display = 'none';
  });

  chrome.runtime.onMessage.addListener((message) => {
    if (message.type === 'progress') {
      // Ensure progress never exceeds 100%
      const progressValue = Math.min(Math.round(message.progress), 100);
      
      // Update progress bar width and text
      progressBar.style.width = `${progressValue}%`;
      progressText.textContent = `검사 진행률: ${progressValue}%`;
      
      if (progressValue === 100) {
        chrome.runtime.sendMessage({ 
          type: 'setState', 
          state: { isAnalyzing: false }
        });
        startButton.style.display = 'block';
        cancelButton.style.display = 'none';
        progressContainer.style.display = 'none';  // Hide progress container when done
      }
    } else if (message.type === 'error') {
      // Handle error cases
      startButton.style.display = 'block';
      cancelButton.style.display = 'none';
      progressContainer.style.display = 'none';
    } else if (message.type === 'stopped') {
      // Handle manual stop
      startButton.style.display = 'block';
      cancelButton.style.display = 'none';
      progressContainer.style.display = 'none';
    }
  });
});