 // Open Chatbot Frame
 function openChatbot() {
    var chatbotFrame = document.getElementById("chatbotFrame");
    chatbotFrame.style.display = "block";
  }

  // Close Chatbot Frame
  function closeChatbot() {
    var chatbotFrame = document.getElementById("chatbotFrame");
    chatbotFrame.style.display = "none";
  }

  // Event Listener for Chat Button
  var chatBtn = document.getElementById("chatBtn");
  chatBtn.addEventListener("click", function(event) {
    event.preventDefault();
    openChatbot();
  });