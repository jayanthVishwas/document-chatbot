import React, { useState, useEffect, useRef, useCallback } from 'react';
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import { MainContainer, ChatContainer, MessageList, Message, MessageInput, TypingIndicator } from '@chatscope/chat-ui-kit-react';

const Chatbot = () => {
  const [messages, setMessages] = useState([
    {
      message: "Whispers of wisdom await... Ask your question!",
      sentTime: "just now",
      sender: "ChatBot",
      style: { fontFamily: 'Courier, monospace' }
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState('');
  const [fileName, setFileName] = useState('');
  const ws = useRef(null);

  // Wrap the function in useCallback to keep its reference stable
  const connectWebSocket = useCallback(() => {
    console.log("Attempting to connect WebSocket...");
    ws.current = new WebSocket("ws://3.82.47.188:8000/ws");

    ws.current.onopen = () => console.log("✅ WebSocket connection established.");

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setMessages((prevMessages) => [
          ...prevMessages,
          {
            message: data.response,
            sentTime: "just now",
            sender: "ChatBot",
            style: { backgroundColor: "green" }
          }
        ]);
      } catch (error) {
        console.error("❌ Error parsing WebSocket message:", error);
      }
      setIsTyping(false);
    };

    ws.current.onerror = (error) => console.error("❌ WebSocket error:", error);

    ws.current.onclose = (event) => {
      console.warn("⚠️ WebSocket closed:", event.code, event.reason);
      if (event.code !== 1000) {
        console.log("🔄 Reconnecting WebSocket in 5 seconds...");
        setTimeout(connectWebSocket, 5000);
      }
    };
  }, []); // No dependencies needed as we're not using any external variables

  useEffect(() => {
    connectWebSocket();
    return () => ws.current?.close();
  }, [connectWebSocket]);

  // Handle Sending Messages
  const handleSend = async (message) => {
    const newMessage = {
      message,
      direction: 'outgoing',
      sender: "user",
      style: { backgroundColor: "blue" }
    };

    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setIsTyping(true);

    if (ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ query: message }));
    } else {
      console.error("⚠️ WebSocket is not open. Retrying...");
      connectWebSocket();
      setTimeout(() => ws.current.send(JSON.stringify({ query: message })), 2000);
    }
  };

  // Handle File Selection
  const handleFileChange = (event) => {
    const files = event.target.files;
    if (files.length > 0) {
      setSelectedFiles(files);
      setFileName(files[0].name);
    }
  };

  // Handle File Upload
  const handleFileUpload = async () => {
    if (selectedFiles.length === 0) {
      setUploadStatus('⚠️ No files selected.');
      return;
    }

    setUploadStatus('⏳ Uploading PDF...');

    const formData = new FormData();
    Array.from(selectedFiles).forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch("http://3.82.47.188:8000/upload_pdfs/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error('Failed to upload files');

      const result = await response.json();
      setUploadStatus('✅ Upload Complete!');
      console.log("Files uploaded successfully:", result);
    } catch (error) {
      setUploadStatus('❌ Error uploading files.');
      console.error("Error uploading files:", error);
    }
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "80vh", padding: "20px" }}>
      {/* PDF Upload Section */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginRight: "40px" }}>
        <input 
          type="file" 
          multiple 
          accept=".pdf" 
          onChange={handleFileChange} 
          style={{ display: 'none' }} 
          id="file-upload"
        />
        <label 
          htmlFor="file-upload" 
          style={{ 
            backgroundColor: "#007bff", 
            color: "white", 
            border: "none", 
            padding: "10px 20px", 
            borderRadius: "4px", 
            cursor: "pointer", 
            marginBottom: "50px",
            width: "150px",
            textAlign: "center" 
          }}
        >
          Upload PDF
        </label>
        {fileName && <p style={{ marginTop: "5px", color: "#007bff" }}>{fileName}</p>}
        <button 
          onClick={handleFileUpload} 
          style={{ 
            backgroundColor: "#007bff", 
            color: "white", 
            border: "none", 
            padding: "10px 20px", 
            borderRadius: "4px", 
            cursor: "pointer",
            width: "150px",
            marginTop: "20px"
          }}
        >
          Submit
        </button>
        {uploadStatus && <p style={{ marginTop: "40px" }}>{uploadStatus}</p>}
      </div>
      
      {/* Chatbox Section */}
      <div style={{ width: "85%", maxWidth: "1100px" }}>
        <div style={{ position: "relative", height: "600px", width: "100%" }}>
          <MainContainer style={{ backgroundColor: "green" }}>
            <ChatContainer style={{ backgroundColor: "green" }}>
              <MessageList
                scrollBehavior="smooth"
                typingIndicator={isTyping ? <TypingIndicator content="ChatBot is typing..." /> : null}
              >
                {messages.map((message, i) => (
                  <Message 
                    key={i} 
                    model={{ 
                      message: message.message, 
                      sentTime: message.sentTime, 
                      sender: message.sender, 
                      style: message.style 
                    }} 
                    className={message.sender === "user" ? "user-message" : "chatbot-message"} 
                  />
                ))}
              </MessageList>
              <MessageInput placeholder="Your curiosity is my command..." onSend={handleSend} attachButton={false} />
            </ChatContainer>
          </MainContainer>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;