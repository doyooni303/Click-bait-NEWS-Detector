// This script runs on news.naver.com pages
(function() {
    // Check if we're on any valid Naver news article page
    function isNewsArticlePage() {
        const url = window.location.href;
        const validNewsPatterns = [
            'n.news.naver.com/article/',
            'm.sports.naver.com/article/',
            'entertain.naver.com/article/'
        ];

        return validNewsPatterns.some(pattern => url.includes(pattern));
    }

    // Send the current URL to the popup
    chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
        if (request.action === "getUrl") {
            sendResponse({
                url: window.location.href,
                isNewsPage: isNewsArticlePage()
            });
        }
    });
})();