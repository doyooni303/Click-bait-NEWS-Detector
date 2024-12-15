let isAnalyzing = false;
let analysisResults = new Map();
const API_BASE_URL = 'http://127.0.0.1:8000';

function getCategory(url) {
  if (url.includes('news.naver.com/section/')) {
    const category = url.split('/section/')[1].split('?')[0];
    const categories = {
      '100': '정치',
      '101': '경제',
      '102': '사회',
      '103': '생활/문화',
      '104': '세계',
      '105': 'IT/과학'
    };
    return categories[category] || null;
  } else if (url.includes('entertain.naver.com')) {
    return '연예';
  } else if (url.includes('sports.news.naver.com')) {
    return '스포츠';
  }
  return null;
}

async function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function analyzeNews() {
  const category = getCategory(window.location.href);
  if (!category) {
    chrome.runtime.sendMessage({ 
      type: 'error', 
      error: '지원되지 않는 페이지입니다.' 
    });
    return;
  }

  try {
    // Extract URLs
    
    const urlResponse = await fetch(`${API_BASE_URL}/BERT/extract-urls`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: window.location.href })
    });
    
    if (!urlResponse.ok) throw new Error('URL 추출 실패');
    
    const { urls } = await urlResponse.json();
    let progress = 0;
    
    // Update state to start analysis
    chrome.runtime.sendMessage({ 
      type: 'setState', 
      state: { isAnalyzing: true, progress: 0 }
    });
    
    for (const url of urls) {
      // Check both local and global state
      if (!isAnalyzing) {
        chrome.runtime.sendMessage({ 
          type: 'stopped',
          state: { isAnalyzing: false }
        });
        break;
      }
      
      try {
        await delay(1000); // 1 second delay

        const response = await fetch(`${API_BASE_URL}/BERT/detect`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url, category })
        });
        
        if (response.ok) {
          const result = await response.json();
          analysisResults.set(url, result);
          attachTooltip(url, result);
        }
      } catch (error) {
        console.error(`Error analyzing ${url}:`, error);
      }
      progress = Math.min(Math.round(((++progress) / urls.length) * 100), 100); // Ensures progress never exceeds 100
      chrome.runtime.sendMessage({ 
        type: 'progress', 
        progress,
        state: { progress } 
      });

      // If analysis is complete, update state
      if (progress === 100) {
        await delay(1000);
        chrome.runtime.sendMessage({ 
          type: 'setState', 
          state: { isAnalyzing: false }
        });
      }
    }
  } catch (error) {
    chrome.runtime.sendMessage({ 
      type: 'error', 
      error: error.message,
      state: { isAnalyzing: false }
    });
  }
}


function attachTooltip(url, result) {
  const newsElements = document.querySelectorAll('a[href*="' + url + '"]');
  newsElements.forEach(element => {
    element.addEventListener('mouseenter', (e) => {
      showTooltip(e, result);
    });
    
    element.addEventListener('mouseleave', () => {
      hideTooltip();
    });
  });
}

function showTooltip(event, result) {
  let tooltip = document.getElementById('clickbait-tooltip');
  if (!tooltip) {
    tooltip = document.createElement('div');
    tooltip.id = 'clickbait-tooltip';
    document.body.appendChild(tooltip);
  }
  
  const consistencyColor = result.prediction === '일치' ? '#03C75A' : '#DC3545';
  
  // tooltip.innerHTML = `
  //   <div class="tooltip-content">
  //     <h3>${result.title}</h3>
  //     <div class="tooltip-details">
  //       <span style="color: ${consistencyColor}">
  //         ${result.prediction} (${result.prob})
  //       </span>
  //     </div>
  //   </div>
  // `;
  tooltip.innerHTML = `
    <div class="tooltip-content">
      <h3>${result.title}</h3>
      <div class="tooltip-details">
        <span style="color: ${consistencyColor}">
          일치성 검사 여부: ${result.prediction} 
        </span>
        <span style="color: ${consistencyColor}">
          일치율: ${result.prob}
        </span>
      </div>
    </div>
  `;
  
  const rect = event.target.getBoundingClientRect();
  tooltip.style.left = `${window.scrollX + rect.right + 10}px`;
  tooltip.style.top = `${window.scrollY + rect.top}px`;
  tooltip.style.display = 'block';
}

function hideTooltip() {
  const tooltip = document.getElementById('clickbait-tooltip');
  if (tooltip) {
    tooltip.style.display = 'none';
  }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'startAnalysis') {
    isAnalyzing = true;
    analyzeNews();
  } else if (message.action === 'stopAnalysis') {
    isAnalyzing = false;
  }
});