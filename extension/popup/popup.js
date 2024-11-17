// document.addEventListener('DOMContentLoaded', function() {
//     const urlDisplay = document.getElementById('currentUrl');
//     const analyzeButton = document.getElementById('analyzeButton');
//     const resultDiv = document.getElementById('result');
//     const loadingDiv = document.getElementById('loading');

//     // Test connection to background script
//     chrome.runtime.sendMessage({action: "test"}, function(response) {
//         console.log("Background connection test:", response);
//     });

//     // Get the current tab's URL
//     chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
//         const currentTab = tabs[0];
        
//         // Send message to content script to check if it's a news page
//         chrome.tabs.sendMessage(currentTab.id, {action: "getUrl"}, function(response) {
//             if (response && response.isNewsPage) {
//                 urlDisplay.textContent = response.url;
//                 analyzeButton.disabled = false;
//             } else {
//                 urlDisplay.textContent = "네이버 뉴스 페이지로 이동하세요";
//                 analyzeButton.disabled = true;
//             }
//         });
//     });

//     // Handle analyze button click
//     analyzeButton.addEventListener('click', async function() {
//         const category = document.querySelector('input[name="category"]:checked')?.value;
        
//         if (!category) {
//             resultDiv.textContent = '카테고리를 선택해주세요.';
//             resultDiv.className = 'error';
//             return;
//         }

//         loadingDiv.style.display = 'block';
//         resultDiv.style.display = 'none';

//         try {
//             const response = await fetch('http://localhost:8000/BERT/detect', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify({
//                     url: urlDisplay.textContent,
//                     category: category
//                 })
//             });

//             const data = await response.json();
            
//             if (response.ok) {
//                 resultDiv.innerHTML = `
//                     <div class="result-card">
//                         <div class="result-header">
//                             <span class="prediction ${data.prediction === 'Fake' ? 'fake' : 'not-fake'}">
//                                 ${data.prediction === 'Fake' ? '낚시성' : '낚시성 아님'} (${data.prob})
//                             </span>
//                         </div>
//                         <div class="meta-info">
//                             <div>제목: ${data.title}</div>
//                             <div>언론사: ${data.press}</div>
//                         </div>
//                     </div>
//                 `;
//             } else {
//                 resultDiv.textContent = '오류가 발생했습니다: ' + (data.detail || '알 수 없는 오류');
//                 resultDiv.className = 'error';
//             }
//         } catch (error) {
//             resultDiv.textContent = '서버 연결 오류가 발생했습니다.';
//             resultDiv.className = 'error';
//         } finally {
//             loadingDiv.style.display = 'none';
//             resultDiv.style.display = 'block';
//         }
//     });
// });

// document.addEventListener('DOMContentLoaded', function() {
//     const form = document.getElementById('newsForm');
//     const analyzeButton = document.querySelector('button[type="submit"]');
//     const resultDiv = document.getElementById('result');
//     const resultsContainer = document.getElementById('results');
//     const loadingDiv = document.getElementById('loading');

//     // Function to check if form is valid
//     function checkFormValidity() {
//         const categorySelected = document.querySelector('input[name="category"]:checked');
//         const isValidUrl = window.location.href.includes('naver.com/article/');
        
//         // Enable/disable button based on selection
//         analyzeButton.disabled = !categorySelected;
        
//         // Update button style
//         if (categorySelected) {
//             analyzeButton.style.backgroundColor = '#03c75a';
//             analyzeButton.style.cursor = 'pointer';
//         } else {
//             analyzeButton.style.backgroundColor = '#cccccc';
//             analyzeButton.style.cursor = 'not-allowed';
//         }
//     }

//     // Add change event listeners to all radio buttons
//     document.querySelectorAll('input[name="category"]').forEach(radio => {
//         radio.addEventListener('change', checkFormValidity);
//     });

//     // Initial check
//     checkFormValidity();

//     // Form submit handler
//     form.addEventListener('submit', async function(e) {
//         e.preventDefault();
        
//         const category = document.querySelector('input[name="category"]:checked')?.value;
        
//         if (!category) {
//             resultDiv.textContent = '카테고리를 선택해주세요.';
//             resultDiv.className = 'error';
//             resultDiv.style.display = 'block';
//             return;
//         }

//         // Get current tab's URL
//         chrome.tabs.query({active: true, currentWindow: true}, async function(tabs) {
//             const currentUrl = tabs[0].url;
            
//             loadingDiv.style.display = 'block';
//             resultDiv.style.display = 'none';
//             resultsContainer.innerHTML = '';
//             analyzeButton.disabled = true;

//             try {
//                 const response = await fetch('http://localhost:8000/BERT/detect', {
//                     method: 'POST',
//                     headers: {
//                         'Content-Type': 'application/json',
//                     },
//                     body: JSON.stringify({
//                         "url": currentUrl,
//                         "category": category
//                     })
//                 });

//                 const data = await response.json();
                
//                 if (response.ok) {
//                     resultsContainer.innerHTML = `
//                         <div class="result-card">
//                             <div class="result-header">
//                                 <span>카테고리: ${category}</span>
//                                 <span class="prediction ${data.prediction === 'Fake' ? 'fake' : 'not-fake'}">
//                                     ${data.prediction === 'Fake' ? '낚시성' : '낚시성 아님'} (${data.prob})
//                                 </span>
//                             </div>
                            
//                             <div class="meta-info">
//                                 <div><strong>제목:</strong> ${data.title || '제목 없음'}</div>
//                                 <div><strong>언론사:</strong> ${data.press || '정보 없음'}</div>
//                                 <div><strong>기자:</strong> ${data.reporter || '정보 없음'}</div>
//                                 <div><strong>작성일:</strong> ${data.date || '정보 없음'}</div>
//                             </div>
//                         </div>
//                     `;
//                     resultDiv.textContent = "분석이 완료되었습니다.";
//                     resultDiv.className = 'success';
//                 } else {
//                     resultDiv.textContent = data.detail || '오류가 발생했습니다.';
//                     resultDiv.className = 'error';
//                 }
//             } catch (error) {
//                 console.error('Error:', error);
//                 resultDiv.textContent = '서버 연결 오류가 발생했습니다.';
//                 resultDiv.className = 'error';
//             } finally {
//                 loadingDiv.style.display = 'none';
//                 resultDiv.style.display = 'block';
//                 analyzeButton.disabled = false;
//             }
//         });
//     });
// });
// document.addEventListener('DOMContentLoaded', function() {
//     console.log('Popup loaded'); // Debug log

//     // Get DOM elements
//     const analyzeButton = document.querySelector('button[type="submit"]');
//     const resultDiv = document.getElementById('result');
//     const loadingDiv = document.getElementById('loading');
//     const resultsContainer = document.getElementById('results');

//     // Enable button when category is selected
//     document.querySelectorAll('input[name="category"]').forEach(radio => {
//         radio.addEventListener('change', function() {
//             console.log('Category selected:', this.value); // Debug log
//             if (analyzeButton) {
//                 analyzeButton.disabled = false;
//                 analyzeButton.style.backgroundColor = '#03c75a';
//             }
//         });
//     });

//     // Add click handler to analyze button
//     if (analyzeButton) {
//         analyzeButton.addEventListener('click', async function(e) {
//             e.preventDefault();
//             console.log('Analyze button clicked'); // Debug log

//             const selectedCategory = document.querySelector('input[name="category"]:checked');
//             if (!selectedCategory) {
//                 alert('카테고리를 선택해주세요.');
//                 return;
//             }

//             // Get current tab URL
//             chrome.tabs.query({active: true, currentWindow: true}, async function(tabs) {
//                 console.log('Current tab:', tabs[0].url); // Debug log
//                 const currentUrl = tabs[0].url;

//                 // Show loading state
//                 if (loadingDiv) loadingDiv.style.display = 'block';
//                 analyzeButton.disabled = true;

//                 try {
//                     console.log('Sending request to server'); // Debug log
//                     const response = await fetch('http://localhost:8000/BERT/detect', {
//                         method: 'POST',
//                         headers: {
//                             'Content-Type': 'application/json',
//                         },
//                         body: JSON.stringify({
//                             url: currentUrl,
//                             category: selectedCategory.value
//                         })
//                     });

//                     console.log('Response received:', response.status); // Debug log
//                     const data = await response.json();
                    
//                     if (response.ok && resultsContainer) {
//                         resultsContainer.innerHTML = `
//                             <div class="result-card">
//                                 <div class="result-header">
//                                     <span>카테고리: ${selectedCategory.value}</span>
//                                     <span class="prediction ${data.prediction === 'Fake' ? 'fake' : 'not-fake'}">
//                                         ${data.prediction === 'Fake' ? '낚시성' : '낚시성 아님'} (${data.prob})
//                                     </span>
//                                 </div>
//                                 <div class="meta-info">
//                                     <div><strong>제목:</strong> ${data.title || '제목 없음'}</div>
//                                     <div><strong>언론사:</strong> ${data.press || '정보 없음'}</div>
//                                     <div><strong>기자:</strong> ${data.reporter || '정보 없음'}</div>
//                                     <div><strong>작성일:</strong> ${data.date || '정보 없음'}</div>
//                                 </div>
//                             </div>
//                         `;
//                     } else {
//                         alert('분석 중 오류가 발생했습니다.');
//                     }
//                 } catch (error) {
//                     console.error('Error:', error); // Debug log
//                     alert('서버 연결 오류가 발생했습니다.');
//                 } finally {
//                     if (loadingDiv) loadingDiv.style.display = 'none';
//                     analyzeButton.disabled = false;
//                 }
//             });
//         });
//     }

//     // Add immediate feedback when clicking radio buttons
//     document.querySelectorAll('.radio-item').forEach(item => {
//         const radio = item.querySelector('input[type="radio"]');
//         const label = item.querySelector('label');
        
//         if (radio && label) {
//             label.addEventListener('click', function() {
//                 // Remove active state from all labels
//                 document.querySelectorAll('.radio-item label').forEach(l => {
//                     l.style.backgroundColor = '';
//                     l.style.borderColor = '#ddd';
//                 });
                
//                 // Add active state to clicked label
//                 this.style.backgroundColor = '#e8f5e9';
//                 this.style.borderColor = '#03c75a';
//             });
//         }
//     });
// });

// 이게 성공한 버젼
// document.addEventListener('DOMContentLoaded', function() {
//     const form = document.getElementById('newsForm');
//     const analyzeButton = document.getElementById('analyzeButton');
//     const resetButton = document.getElementById('resetButton');
//     const loadingDiv = document.getElementById('loading');
//     const resultDiv = document.getElementById('result');
//     const resultsContainer = document.getElementById('results');

//     // Enable analyze button when a category is selected
//     document.querySelectorAll('input[name="category"]').forEach(radio => {
//         radio.addEventListener('change', function() {
//             analyzeButton.disabled = false;
//             analyzeButton.style.backgroundColor = '#03c75a';
//         });
//     });

//     // Reset functionality
//     resetButton.addEventListener('click', function() {
//         form.reset();
//         analyzeButton.disabled = true;
//         analyzeButton.style.backgroundColor = '#cccccc';
//         resultsContainer.innerHTML = '';
//         resultDiv.style.display = 'none';
//         resetButton.style.display = 'none';
//     });

//     // Form submission
//     form.addEventListener('submit', async function(e) {
//         e.preventDefault();
        
//         const selectedCategory = document.querySelector('input[name="category"]:checked');
//         if (!selectedCategory) {
//             alert('카테고리를 선택해주세요.');
//             return;
//         }

//         // Get current tab URL
//         chrome.tabs.query({active: true, currentWindow: true}, async function(tabs) {
//             const currentUrl = tabs[0].url;
            
//             loadingDiv.style.display = 'block';
//             analyzeButton.disabled = true;

//             try {
//                 const response = await fetch('http://localhost:8000/BERT/detect', {
//                     method: 'POST',
//                     headers: {
//                         'Content-Type': 'application/json',
//                     },
//                     body: JSON.stringify({
//                         url: currentUrl,
//                         category: selectedCategory.value
//                     })
//                 });

//                 const data = await response.json();
                
//                 if (response.ok) {
//                     resultsContainer.innerHTML = `
//                         <div class="result-card">
//                             <div class="result-header">
//                                 <span>카테고리: ${selectedCategory.value}</span>
//                                 <span class="prediction ${data.prediction === 'Fake' ? 'fake' : 'not-fake'}">
//                                     ${data.prediction === 'Fake' ? '낚시성' : '낚시성 아님'} (${data.prob})
//                                 </span>
//                             </div>
//                             <div class="meta-info">
//                                 <div><strong>제목:</strong> ${data.title || '제목 없음'}</div>
//                                 <div><strong>언론사:</strong> ${data.press || '정보 없음'}</div>
//                                 <div><strong>기자:</strong> ${data.reporter || '정보 없음'}</div>
//                                 <div><strong>작성일:</strong> ${data.date || '정보 없음'}</div>
//                             </div>
//                         </div>
//                     `;
//                     resetButton.style.display = 'block';
//                 } else {
//                     resultDiv.textContent = data.detail || '오류가 발생했습니다.';
//                     resultDiv.className = 'error';
//                     resultDiv.style.display = 'block';
//                 }
//             } catch (error) {
//                 console.error('Error:', error);
//                 resultDiv.textContent = '서버 연결 오류가 발생했습니다.';
//                 resultDiv.className = 'error';
//                 resultDiv.style.display = 'block';
//             } finally {
//                 loadingDiv.style.display = 'none';
//                 analyzeButton.disabled = false;
//             }
//         });
//     });
// });


document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('newsForm');
    const analyzeButton = document.getElementById('analyzeButton');
    const resetButton = document.getElementById('resetButton');
    const loadingDiv = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    const resultsContainer = document.getElementById('results');

    function createShareButtons(data, currentUrl) {
        const shareText = `
    [낚시성 뉴스 기사 탐지 결과]
    제목: ${data.title}
    분석 결과: ${data.prediction === 'Fake' ? '낚시성' : '낚시성 아님'} (${data.prob})
    언론사: ${data.press}
    카테고리: ${document.querySelector('input[name="category"]:checked').value}
    작성일: ${data.date}
    `;

        // Copy button functionality
        document.getElementById('copyButton').addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(shareText);
                const button = document.getElementById('copyButton');
                button.textContent = '복사완료!';
                button.classList.add('copy-success');
                setTimeout(() => {
                    button.textContent = '복사하기';
                    button.classList.remove('copy-success');
                }, 2000);
            } catch (err) {
                console.error('Failed to copy text:', err);
            }
        });

    }

    // Enable analyze button when a category is selected
    document.querySelectorAll('input[name="category"]').forEach(radio => {
        radio.addEventListener('change', function() {
            analyzeButton.disabled = false;
            analyzeButton.style.backgroundColor = '#03c75a';
        });
    });

    // Reset functionality
    resetButton.addEventListener('click', function() {
        form.reset();
        analyzeButton.disabled = true;
        analyzeButton.style.backgroundColor = '#cccccc';
        resultsContainer.innerHTML = '';
        resultDiv.style.display = 'none';
        resetButton.style.display = 'none';
    });

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const selectedCategory = document.querySelector('input[name="category"]:checked');
        if (!selectedCategory) {
            alert('카테고리를 선택해주세요.');
            return;
        }

        // Get current tab URL
        chrome.tabs.query({active: true, currentWindow: true}, async function(tabs) {
            const currentUrl = tabs[0].url;
            
            loadingDiv.style.display = 'block';
            analyzeButton.disabled = true;

            try {
                const response = await fetch('http://localhost:8000/BERT/detect', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        url: currentUrl,
                        category: selectedCategory.value
                    })
                });

                const data = await response.json();
                
                if (response.ok) {
                    resultsContainer.innerHTML = `
                        <div class="result-card">
                            <div class="result-header">
                                <span>카테고리: ${selectedCategory.value}</span>
                                <span class="prediction ${data.prediction === 'Fake' ? 'fake' : 'not-fake'}">
                                    ${data.prediction === 'Fake' ? '낚시성' : '낚시성 아님'} (${data.prob})
                                </span>
                            </div>
                            <div class="meta-info">
                                <div><strong>제목:</strong> ${data.title || '제목 없음'}</div>
                                <div><strong>언론사:</strong> ${data.press || '정보 없음'}</div>
                                <div><strong>기자:</strong> ${data.reporter || '정보 없음'}</div>
                                <div><strong>작성일:</strong> ${data.date || '정보 없음'}</div>
                            </div>
                            <div class="share-buttons">
                                <button id="copyButton" class="share-button" title="클립보드에 복사">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                                    </svg>
                                    복사하기
                                </button>
                            </div>
                        </div>
                    `;
                    resetButton.style.display = 'block';
                    
                    // Initialize share buttons
                    createShareButtons(data, currentUrl);
                } else {
                    resultDiv.textContent = data.detail || '오류가 발생했습니다.';
                    resultDiv.className = 'error';
                    resultDiv.style.display = 'block';
                }
            } catch (error) {
                console.error('Error:', error);
                resultDiv.textContent = '서버 연결 오류가 발생했습니다.';
                resultDiv.className = 'error';
                resultDiv.style.display = 'block';
            } finally {
                loadingDiv.style.display = 'none';
                analyzeButton.disabled = false;
            }
        });
    });
});