document.addEventListener('DOMContentLoaded', function() {
  const chatMessages = document.getElementById('chat-messages');
  const userInput = document.getElementById('user-input');
  const sendBtn = document.getElementById('send-btn');
  const languageSelect = document.getElementById('language-select');

  // Rasa server URL - update this with your deployed Rasa server
  const RASA_SERVER_URL = 'http://localhost:5005/webhooks/rest/webhook';
  
  // Check if Rasa server is reachable
  fetch(RASA_SERVER_URL.replace('/webhooks/rest/webhook', '/version'))
    .then(response => {
      if (response.ok) {
        addMessage("✅ Connected to Rasa server successfully!", false);
      } else {
        addMessage("⚠️ Connected to Rasa server but received error status: " + response.status, false);
      }
    })
    .catch(error => {
      addMessage("❌ Failed to connect to Rasa server: " + error.message, false);
      console.error("Connection error:", error);
    });

  // Function to handle language selection
  function handleLanguageSelection() {
    const selectedLanguage = languageSelect.value;
    const languageSections = document.querySelectorAll('.language-section');
    
    languageSections.forEach(section => {
      if (selectedLanguage === 'all') {
        section.style.display = 'block';
      } else {
        if (section.classList.contains(selectedLanguage)) {
          section.style.display = 'block';
        } else {
          section.style.display = 'none';
        }
      }
    });
  }

  // Initialize language selection
  handleLanguageSelection();
  
  // Add event listener for language selection change
  languageSelect.addEventListener('change', handleLanguageSelection);

  // Function to add messages to the chat
  function addMessage(message, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    if (isUser) {
      // User messages are simple
      messageContent.innerHTML = message;
    } else {
      // Try to parse and format bot messages that have multilingual responses
      // This is a simple approach that assumes a specific format from the LLM
      // You may need to adjust this based on actual response format
      
      if (message.includes("ଓଡ଼ିଆ") || message.includes("हिंदी") || message.includes("English:")) {
        // Attempt to split by language markers
        let odiaSection = "";
        let hindiSection = "";
        let englishSection = "";
        
        // Extract Odia section if present
        const odiaMatch = message.match(/ଓଡ଼ିଆ[:\s]*([\s\S]*?)(?=हिंदी|\nEnglish:|$)/i);
        if (odiaMatch && odiaMatch[1]) {
          odiaSection = `<div class="language-section odia">
            <strong>ଓଡ଼ିଆ:</strong><br>
            ${odiaMatch[1].trim()}
          </div>`;
        }
        
        // Extract Hindi section if present
        const hindiMatch = message.match(/हिंदी[:\s]*([\s\S]*?)(?=\nEnglish:|ଓଡ଼ିଆ|$)/i);
        if (hindiMatch && hindiMatch[1]) {
          hindiSection = `<div class="language-section hindi">
            <strong>हिंदी:</strong><br>
            ${hindiMatch[1].trim()}
          </div>`;
        }
        
        // Extract English section if present
        const englishMatch = message.match(/English[:\s]*([\s\S]*?)(?=ଓଡ଼ିଆ|हिंदी|$)/i);
        if (englishMatch && englishMatch[1]) {
          englishSection = `<div class="language-section english">
            <strong>English:</strong><br>
            ${englishMatch[1].trim()}
          </div>`;
        }
        
        // Combine all sections
        messageContent.innerHTML = odiaSection + hindiSection + englishSection;
      } else {
        // For responses without clear language sections, just display as is
        messageContent.innerHTML = message;
      }
    }
    
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    
    // Apply language filtering
    handleLanguageSelection();
    
    // Scroll to the bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Function to send message to Rasa
  async function sendMessage(message) {
    try {
      console.log("Sending message to:", RASA_SERVER_URL);
      
      // Create XMLHttpRequest for better browser compatibility
      const xhr = new XMLHttpRequest();
      xhr.open('POST', RASA_SERVER_URL, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      
      xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
          console.log("Response status:", xhr.status);
          try {
            const data = JSON.parse(xhr.responseText);
            console.log("Response data:", data);
            
            // Display bot responses
            if (data && data.length > 0) {
              data.forEach(msg => {
                if (msg.text) {
                  addMessage(msg.text, false);
                }
              });
            } else {
              addMessage("⚠️ I received an empty response. Please try a different question.", false);
            }
          } catch (parseError) {
            console.error("Error parsing JSON:", parseError);
            addMessage("❌ Error parsing response: " + parseError.message, false);
          }
        } else {
          console.error('HTTP Error:', xhr.status, xhr.statusText);
          addMessage("❌ HTTP Error " + xhr.status + ": " + xhr.statusText, false);
        }
      };
      
      xhr.onerror = function() {
        console.error('Network Error');
        addMessage("❌ Network error: Cannot connect to the Rasa server at " + RASA_SERVER_URL + ". Make sure all services are running.", false);
      };
      
      xhr.send(JSON.stringify({
        sender: 'user',
        message: message
      }));
    } catch (error) {
      console.error('Error:', error);
      addMessage("❌ Error: " + error.message, false);
    }
  }

  // Event listeners
  sendBtn.addEventListener('click', function() {
    const message = userInput.value.trim();
    if (message) {
      addMessage(message, true);
      sendMessage(message);
      userInput.value = '';
    }
  });

  userInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      const message = userInput.value.trim();
      if (message) {
        addMessage(message, true);
        sendMessage(message);
        userInput.value = '';
      }
    }
  });
});