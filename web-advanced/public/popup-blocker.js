// Aggressive popup blocker for persistent "Model can't be changed" messages
(function() {
  'use strict';
  
  let blockedCount = 0;
  const maxBlocked = 100;
  
  // Function to remove elements containing specific text
  function removeElementsWithText(text) {
    if (blockedCount >= maxBlocked) return;
    
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      null,
      false
    );
    
    const textNodes = [];
    let node;
    
    while (node = walker.nextNode()) {
      if (node.textContent.includes(text)) {
        textNodes.push(node);
      }
    }
    
    textNodes.forEach(textNode => {
      let element = textNode.parentElement;
      while (element && element !== document.body) {
        if (element.style.position === 'fixed' || 
            element.style.position === 'absolute' ||
            element.className.includes('popup') ||
            element.className.includes('modal') ||
            element.className.includes('notification') ||
            element.className.includes('toast')) {
          element.remove();
          blockedCount++;
          console.log('Blocked popup:', text);
          break;
        }
        element = element.parentElement;
      }
    });
  }
  
  // Function to block specific popups
  function blockPopups() {
    const targetTexts = [
      "Model can't be changed",
      "model can't be changed",
      "To switch models",
      "start a new chat",
      "choose the model manually"
    ];
    
    targetTexts.forEach(text => {
      removeElementsWithText(text);
    });
  }
  
  // Override common popup methods
  const originalAlert = window.alert;
  const originalConfirm = window.confirm;
  
  window.alert = function(message) {
    if (typeof message === 'string' && 
        (message.includes("Model can't be changed") || 
         message.includes("model") || 
         message.includes("chat"))) {
      console.log('Blocked alert popup:', message);
      return;
    }
    return originalAlert.call(this, message);
  };
  
  window.confirm = function(message) {
    if (typeof message === 'string' && 
        (message.includes("Model can't be changed") || 
         message.includes("model") || 
         message.includes("chat"))) {
      console.log('Blocked confirm popup:', message);
      return false;
    }
    return originalConfirm.call(this, message);
  };
  
  // Run immediately and set up intervals
  blockPopups();
  
  // Check every 100ms for new popups
  const interval = setInterval(() => {
    if (blockedCount >= maxBlocked) {
      clearInterval(interval);
      console.log('Popup blocker stopped after blocking', blockedCount, 'popups');
      return;
    }
    blockPopups();
  }, 100);
  
  // Set up mutation observer for dynamic content
  const observer = new MutationObserver((mutations) => {
    if (blockedCount >= maxBlocked) {
      observer.disconnect();
      return;
    }
    
    mutations.forEach((mutation) => {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === 1) {
          const element = node;
          
          // Check if the element or its children contain the target text
          if (element.textContent && 
              element.textContent.includes("Model can't be changed")) {
            element.remove();
            blockedCount++;
            console.log('Blocked dynamically added popup');
          }
          
          // Check for suspicious popup-like elements
          if (element.style && 
              (element.style.position === 'fixed' || 
               element.style.position === 'absolute') &&
              element.style.zIndex > 1000) {
            if (element.textContent && 
                (element.textContent.includes("model") || 
                 element.textContent.includes("chat"))) {
              element.remove();
              blockedCount++;
              console.log('Blocked suspicious popup element');
            }
          }
        }
      });
    });
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
  
  // Clean up after 30 seconds
  setTimeout(() => {
    clearInterval(interval);
    observer.disconnect();
    console.log('Popup blocker cleanup completed');
  }, 30000);
  
})();