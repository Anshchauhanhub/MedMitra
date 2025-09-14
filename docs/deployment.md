# Running and Deploying MedMitra

This guide will help you run MedMitra locally and deploy it to production environments.

## Running Locally

### Prerequisites
- Python 3.8 or higher
- Rasa 3.x installed
- API key for Gemini or alternative LLM

### Steps to Run

1. **Activate your virtual environment**:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Train the Rasa model**:
   ```bash
   rasa train
   ```
   This will create a model file in the `models/` directory.

3. **Start the Action Server** (in a separate terminal window):
   ```bash
   rasa run actions
   ```
   This will start the action server on port 5055.

4. **Start the Rasa Server**:
   
   For command-line testing:
   ```bash
   rasa shell
   ```
   
   For API mode:
   ```bash
   rasa run --enable-api --cors "*" --debug
   ```
   This will start the Rasa server on port 5005.

## Deployment Options

### Option 1: Docker Deployment

1. Create a Dockerfile in the root directory:
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .

   # Command to run the Rasa server
   CMD ["rasa", "run", "--enable-api", "--cors", "*"]
   ```

2. Create a docker-compose.yml file:
   ```yaml
   version: '3.0'
   services:
     rasa:
       build: .
       ports:
         - "5005:5005"
       volumes:
         - ./models:/app/models
       environment:
         - GEMINI_API_KEY=${GEMINI_API_KEY}
       command: ["rasa", "run", "--enable-api", "--cors", "*"]
       depends_on:
         - "rasa-actions"
       networks:
         - rasa-network

     rasa-actions:
       build: .
       ports:
         - "5055:5055"
       volumes:
         - ./actions:/app/actions
       environment:
         - GEMINI_API_KEY=${GEMINI_API_KEY}
       command: ["rasa", "run", "actions"]
       networks:
         - rasa-network

   networks:
     rasa-network:
       driver: bridge
   ```

3. Build and run the Docker containers:
   ```bash
   docker-compose up -d
   ```

### Option 2: Cloud Deployment

#### Heroku Deployment

1. Create a Procfile in the root directory:
   ```
   web: rasa run --enable-api --cors "*" --port $PORT
   worker: rasa run actions
   ```

2. Deploy to Heroku:
   ```bash
   heroku create medmitra
   git push heroku master
   heroku config:set GEMINI_API_KEY=your_api_key_here
   ```

#### AWS Deployment

1. Set up an EC2 instance with Docker installed
2. Clone your repository and use Docker Compose as described above
3. Set up an Application Load Balancer for routing traffic

## Creating a Simple Web Interface

You can create a simple web interface for MedMitra using HTML, CSS, and JavaScript. Here's a basic example:

1. Create a new directory called `webchat` in your project:
   ```bash
   mkdir -p webchat
   ```

2. Create an index.html file:
   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
     <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <title>MedMitra - Healthcare Assistant</title>
     <link rel="stylesheet" href="styles.css">
   </head>
   <body>
     <div class="chat-container">
       <div class="chat-header">
         <h1>MedMitra</h1>
         <p>Your Healthcare Education Assistant</p>
       </div>
       <div class="chat-messages" id="chat-messages">
         <div class="message bot">
           <div class="message-content">
             नमस्ते! मैं MedMitra हूँ, आपका स्वास्थ्य सहायक। मैं आपको निवारक स्वास्थ्य देखभाल, बीमारी के लक्षण और टीकाकरण अनुसूची के बारे में जानकारी दे सकता हूँ। मैं आपकी कैसे मदद कर सकता हूँ?<br><br>
             Hello! I am MedMitra, your health assistant. I can provide information about preventive healthcare, disease symptoms, and vaccination schedules. How can I help you today?
           </div>
         </div>
       </div>
       <div class="chat-input">
         <input type="text" id="user-input" placeholder="Type your health question here...">
         <button id="send-btn">Send</button>
       </div>
     </div>
     <script src="script.js"></script>
   </body>
   </html>
   ```

3. Create a styles.css file:
   ```css
   * {
     margin: 0;
     padding: 0;
     box-sizing: border-box;
     font-family: Arial, sans-serif;
   }

   body {
     background-color: #f5f5f5;
     display: flex;
     justify-content: center;
     align-items: center;
     min-height: 100vh;
   }

   .chat-container {
     width: 100%;
     max-width: 600px;
     background-color: white;
     border-radius: 10px;
     box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
     overflow: hidden;
     display: flex;
     flex-direction: column;
     height: 80vh;
   }

   .chat-header {
     background-color: #4285f4;
     color: white;
     padding: 15px;
     text-align: center;
   }

   .chat-header h1 {
     font-size: 24px;
     margin-bottom: 5px;
   }

   .chat-messages {
     flex: 1;
     padding: 15px;
     overflow-y: auto;
   }

   .message {
     margin-bottom: 15px;
     display: flex;
     flex-direction: column;
   }

   .user {
     align-items: flex-end;
   }

   .bot {
     align-items: flex-start;
   }

   .message-content {
     padding: 10px 15px;
     border-radius: 10px;
     max-width: 80%;
   }

   .user .message-content {
     background-color: #e3f2fd;
   }

   .bot .message-content {
     background-color: #f5f5f5;
   }

   .chat-input {
     display: flex;
     padding: 15px;
     border-top: 1px solid #e0e0e0;
   }

   #user-input {
     flex: 1;
     padding: 10px;
     border: 1px solid #e0e0e0;
     border-radius: 5px;
     outline: none;
   }

   #send-btn {
     padding: 10px 15px;
     background-color: #4285f4;
     color: white;
     border: none;
     border-radius: 5px;
     margin-left: 10px;
     cursor: pointer;
   }

   #send-btn:hover {
     background-color: #3367d6;
   }
   ```

4. Create a script.js file:
   ```javascript
   document.addEventListener('DOMContentLoaded', function() {
     const chatMessages = document.getElementById('chat-messages');
     const userInput = document.getElementById('user-input');
     const sendBtn = document.getElementById('send-btn');

     // Rasa server URL - update this with your deployed Rasa server
     const RASA_SERVER_URL = 'http://localhost:5005/webhooks/rest/webhook';

     // Function to add messages to the chat
     function addMessage(message, isUser) {
       const messageDiv = document.createElement('div');
       messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
       
       const messageContent = document.createElement('div');
       messageContent.className = 'message-content';
       messageContent.innerHTML = message;
       
       messageDiv.appendChild(messageContent);
       chatMessages.appendChild(messageDiv);
       
       // Scroll to the bottom
       chatMessages.scrollTop = chatMessages.scrollHeight;
     }

     // Function to send message to Rasa
     async function sendMessage(message) {
       try {
         const response = await fetch(RASA_SERVER_URL, {
           method: 'POST',
           headers: {
             'Content-Type': 'application/json',
           },
           body: JSON.stringify({
             sender: 'user',
             message: message
           }),
         });
         
         const data = await response.json();
         
         // Display bot responses
         if (data && data.length > 0) {
           data.forEach(msg => {
             if (msg.text) {
               addMessage(msg.text, false);
             }
           });
         } else {
           addMessage("I'm sorry, I'm having trouble responding. Please try again.", false);
         }
       } catch (error) {
         console.error('Error:', error);
         addMessage("I'm sorry, I couldn't connect to the server. Please try again later.", false);
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
   ```

To use this web interface, serve it with a simple HTTP server and ensure your Rasa server is running with CORS enabled.

## Troubleshooting

### Common Issues and Solutions

1. **API Key Issues**:
   - Check that your API key is correctly set in the .env file
   - Verify the environment variable is being loaded correctly

2. **Action Server Connection Failures**:
   - Ensure the action server is running on port 5055
   - Check endpoints.yml has the correct URL

3. **Training Errors**:
   - Verify the format of your training data files
   - Check for syntax errors in yaml files

4. **Deployment Issues**:
   - Check network configurations and firewall settings
   - Ensure Docker has enough resources allocated

For more help, refer to the [Rasa documentation](https://rasa.com/docs/).