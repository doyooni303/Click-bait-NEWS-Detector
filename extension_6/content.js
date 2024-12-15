let isAnalyzing = false;
let analysisResults = new Map();
const API_BASE_URL = 'http://127.0.0.1:8000';
const tooltipStyles = `
  #clickbait-tooltip {
    position: absolute;
    z-index: 10000;
    background-color: white;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 12px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
    max-width: 300px;
    font-family: 'NanumSquare', sans-serif;
  }

  .tooltip-content h3 {
    margin: 0 0 8px 0;
    font-size: 14px;
    font-weight: bold;
    color: #333;
  }

  .tooltip-details {
    font-size: 13px;
    line-height: 1.5;
  }
`;



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
    const urlResponse = await fetch(`${API_BASE_URL}/BERT/extract-urls`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: window.location.href })
    });
    
    if (!urlResponse.ok) throw new Error('URL 추출 실패');
    
    const { urls } = await urlResponse.json();
    let progress = 0;
    
    chrome.runtime.sendMessage({ 
      type: 'setState', 
      state: { isAnalyzing: true, progress: 0 }
    });
    
    for (const url of urls) {
      if (!isAnalyzing) {
        chrome.runtime.sendMessage({ 
          type: 'stopped',
          state: { isAnalyzing: false }
        });
        break;
      }
      
      try {
        await delay(300);  // Reduced initial delay

        const response = await fetch(`${API_BASE_URL}/BERT/detect`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url, category })
        });
        
        if (response.ok) {
          const result = await response.json();

          // Store result first
          analysisResults.set(url, result);

          // Update progress and title immediately after getting result
          const currentProgress = Math.round(((analysisResults.size) / urls.length) * 100);
          chrome.runtime.sendMessage({ 
            type: 'progress', 
            progress: currentProgress,
            title: result.title
          });

          // Attach tooltip in background without waiting
          attachTooltip(url, result).catch(error => {
            console.error('Error attaching tooltip:', error);
          });

          // Minimal delay between requests
          await delay(200);
        }
      } catch (error) {
        console.error(`Error analyzing ${url}:`, error);
      }

      if (analysisResults.size === urls.length) {
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
  
  // Create elements manually instead of using innerHTML
  const tooltipContent = document.createElement('div');
  tooltipContent.className = 'tooltip-content';

  const titleElement = document.createElement('h3');
  titleElement.textContent = result.title;  // textContent handles encoding automatically

  const detailsDiv = document.createElement('div');
  detailsDiv.className = 'tooltip-details';

  const predictionSpan = document.createElement('span');
  predictionSpan.style.color = consistencyColor;
  predictionSpan.textContent = `결과: ${result.prediction}`;

  const probSpan = document.createElement('span');
  probSpan.style.color = consistencyColor;
  probSpan.textContent = `일치율: ${result.prob}`;

  // Assemble the tooltip
  detailsDiv.appendChild(predictionSpan);
  detailsDiv.appendChild(document.createElement('br'));  // Add line break
  detailsDiv.appendChild(probSpan);
  
  tooltipContent.appendChild(titleElement);
  tooltipContent.appendChild(detailsDiv);

  // Clear and update tooltip
  tooltip.innerHTML = '';
  tooltip.appendChild(tooltipContent);

  // Position the tooltip
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

// Add styles to document
const styleSheet = document.createElement('style');
styleSheet.textContent = tooltipStyles;
document.head.appendChild(styleSheet);