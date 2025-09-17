// Smooth scrolling navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      // Ignore if not a navigation link
      if (!this.getAttribute('href').startsWith('#') || this.getAttribute('href') === "#") return;
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({behavior: 'smooth', block: 'start'});
      }
    });
  });
  
  // Chatbot implementation
  let chatbotOpen = false;
  
  function toggleChatbot() {
    const windowEl = document.getElementById('chatbot-window');
    chatbotOpen = !chatbotOpen;
    windowEl.style.display = chatbotOpen ? 'flex' : 'none';
    if (chatbotOpen) {
      document.getElementById('user-input').focus();
    }
  }
  
  function handleKeyPress(event) {
    if (event.key === 'Enter') sendMessage();
  }
  
  function sendMessage() {
    const input = document.getElementById('user-input');
    let message = input.value.trim();
    if (!message) return;
    addMessage(message, 'user');
    input.value = '';
    setTimeout(() => addMessage(getBotResponse(message), 'bot'), 600);
  }
  
  function sendQuickMessage(msg) {
    addMessage(msg, 'user');
    setTimeout(() => addMessage(getBotResponse(msg), 'bot'), 600);
  }
  
  // Simple local logic; replace with your actual AI API integration.
  function getBotResponse(message) {
    const lc = message.toLowerCase();
    if (lc.includes('hospital')) return "🏥 To find hospitals, visit the Health Services section or call 108 in emergency.";
    if (lc.includes('vaccine')) return "💉 Visit the Vaccination Portal to book appointments. Need COVID or other vaccines?";
    if (lc.includes('emergency')) return "🚨 Emergency Numbers: 108 (Ambulance), 102 (Health), 1075 (Integrated Helpline).";
    if (lc.includes('scheme')) return "📋 Major Health Schemes: Ayushman Bharat, Jan Aarogya Yojana. Want more info?";
    return "🤖 Thank you for your query. For medical emergencies, call our helpline or consult a doctor for advice!";
  }
  
  function addMessage(text, sender) {
    const messagesContainer = document.getElementById('chatbot-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = `<p>${text}</p>`;
    messageDiv.appendChild(bubble);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
  
  // Service card interactivity (if needed)
  // document.querySelectorAll('.service-card').forEach(card =>
  //   card.addEventListener('click', (e) => { /* Modal logic or navigation */ })
  // );
  
  // Modal logic can be added similarly.
  
  // Dummy downloadApp function
  function downloadApp(platform) {
    if (platform === 'ios') alert('App Store link coming soon!');
    if (platform === 'android') alert('Google Play link coming soon!');
  }
  