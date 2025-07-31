"use client";
import React, { useState, useRef, useEffect } from "react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { v4 as uuidv4 } from "uuid";
import { getInitialTheme } from "@/lib/utils";
import { Ellipsis, SendHorizontal, RotateCcw } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

function getSessionId() {
  // Try to persist session_id in localStorage for the session
  if (typeof window === "undefined") return "";
  let sessionId = localStorage.getItem("airtel-chatbot-session-id");
  if (!sessionId) {
    sessionId = uuidv4();
    // sessionId = crypto.randomUUID();
    // sessionId = "1234567890";
    localStorage.setItem("airtel-chatbot-session-id", sessionId);
  }
  return sessionId;
}

export default function Chat() {
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [currentTheme, setCurrentTheme] = useState<'light' | 'dark'>('light');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [hasError, setHasError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const [sessionId, setSessionId] = useState<string>("");
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [streamingMessage, setStreamingMessage] = useState<string>("");
  const eventSourceRef = useRef<EventSource | null>(null);

  // Set initial theme based on localStorage or system preference
  useEffect(() => {
    setCurrentTheme(getInitialTheme());
    setMounted(true);
  }, []);

  // Update theme when resolvedTheme changes
  useEffect(() => {
    if (resolvedTheme && (resolvedTheme === 'light' || resolvedTheme === 'dark')) {
      setCurrentTheme(resolvedTheme);
    }
  }, [resolvedTheme]);

  useEffect(() => {
    setSessionId(getSessionId());
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingMessage]);

  useEffect(() => {
    if (mounted && inputRef.current) {
      inputRef.current.focus();
    }
  }, [mounted, messages, isLoading, currentTheme]);

  // Clean up event source on component unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const handleSendStreaming = async () => {
    if (!input.trim() || !sessionId) return;
    setHasError(null);
    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setStreamingMessage("");
    inputRef.current?.focus();

    try {
      // Close any existing event source
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      // Create a new EventSource for SSE
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: userMessage.content, 
          session_id: sessionId,
          stream: true 
        }),
      });

      // Handle streaming response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) {
        throw new Error("Failed to get response reader");
      }
      
      // Start reading the stream
      let accumulatedResponse = "";
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }
        
        // Decode the chunk and process SSE format
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.substring(6);
            
            // Check for completion marker
            if (data === '[DONE]') {
              // Finalize the message
              setMessages(prev => [
                ...prev.slice(0, -1), 
                { role: "user", content: userMessage.content },
                { role: "assistant", content: accumulatedResponse }
              ]);
              setStreamingMessage("");
              break;
            } else {
              // Accumulate the response
              accumulatedResponse += data;
              setStreamingMessage(accumulatedResponse);
            }
          }
        }
      }
    } catch (err) {
      const error = err as Error;
      setHasError(error.message || "Unknown error");
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleSend = async () => {
    // Use streaming by default
    await handleSendStreaming();
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleRestart = async () => {
    setMessages([]);
    setStreamingMessage("");
    setHasError(null);
    
    // Close any existing event source
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    // Generate new session ID
    const newSessionId = uuidv4();
    setSessionId(newSessionId);
    if (typeof window !== "undefined") {
      localStorage.setItem("airtel-chatbot-session-id", newSessionId);
    }
    
    // Clear session on the server
    try {
      await fetch(`/api/chat/${sessionId}`, { method: "DELETE" });
    } catch (err) {
      console.error("Failed to clear session:", err);
    }
    
    inputRef.current?.focus();
  };

  // Use the skeleton loader only for a very brief moment during initial load
  if (!mounted) {
    return (
      <div className="flex flex-col w-full max-w-2xl h-[32rem] rounded-xl items-center justify-between bg-gray-200 shadow-lg p-4 animate-pulse">
        {/* Skeleton loader */}
        <div className="flex-1 w-full flex flex-col space-y-4 py-4">
          <div className="w-3/4 h-8 bg-gray-300 rounded-lg self-start"></div>
          <div className="w-2/3 h-8 bg-gray-300 rounded-lg self-end"></div>
          <div className="w-3/4 h-8 bg-gray-300 rounded-lg self-start"></div>
        </div>
        <div className="w-full flex gap-2 items-center">
          <div className="flex-1 h-10 bg-gray-300 rounded-md"></div>
          <div className="h-10 w-16 bg-gray-300 rounded-md"></div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`flex flex-col w-full max-w-2xl h-[32rem] rounded-xl items-center justify-between ${
        currentTheme === "dark"
          ? "bg-white text-[#E31F26]"
          : "bg-[#E31F26] text-white"
      } shadow-lg p-4 transition-colors duration-300`}
    >
      {/* Restart chat button */}
      <div className="flex justify-start mb-2 w-full">
        {messages.length > 0 && (
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={handleRestart}
            title="Restart Chat"
            disabled={isLoading}
          >
            <RotateCcw />
          </Button>
        )}
      </div>
      {/* Messages area */}
      <div
        className={
          "flex-1 w-full overflow-y-auto px-2 mb-2 space-y-2 airtel-chat-scrollbar"
        }
        aria-label="Chat messages"
        tabIndex={0}
        style={{ minHeight: 0 }}
      >
        {messages.length === 0 && !streamingMessage && (
          <div className="flex items-center justify-center h-full text-center text-base opacity-60">
            Start the conversation!
          </div>
        )}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex w-full ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`rounded-lg px-4 py-2 max-w-[80%] break-words whitespace-pre-wrap text-sm shadow-md ${
                msg.role === "user"
                  ? currentTheme === "dark"
                    ? "bg-[#E31F26] text-white"
                    : "bg-white text-[#E31F26]"
                  : currentTheme === "dark"
                  ? "bg-gray-100 text-[#E31F26]"
                  : "bg-[#fff7f7] text-[#E31F26]"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {/* Streaming message */}
        {streamingMessage && (
          <div className="flex w-full justify-start">
            <div
              className={`rounded-lg px-4 py-2 max-w-[80%] break-words text-sm shadow-md ${
                currentTheme === "dark"
                  ? "bg-gray-100 text-[#E31F26]"
                  : "bg-[#fff7f7] text-[#E31F26]"
              }`}
            >
              {streamingMessage}
            </div>
          </div>
        )}
        {/* Loading spinner - only show when no streaming message */}
        {isLoading && !streamingMessage && (
          <div className="flex w-full justify-start">
            <div
              className={`rounded-lg px-4 py-2 max-w-[80%] shadow-md ${
                currentTheme === "dark"
                  ? "bg-gray-100 text-[#E31F26]"
                  : "bg-[#fff7f7] text-[#E31F26]"
              }`}
            >
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent"></div>
                <span className="text-sm">Airtel is typing...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      {/* Error message */}
      {hasError && (
        <div className={`w-full text-center text-xs mb-2 ${ currentTheme === "dark" ? "text-red-600" : "text-white" }`}>{hasError}</div>
      )}
      {/* Input area */}
      <form
        className="flex w-full gap-2 items-center"
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
      >
        <Input
          type="text"
          className={`flex-1 rounded-md px-3 py-2 text-base border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#E31F26] ${ currentTheme === "dark" ? "placeholder:text-[#E31F26]" : "placeholder:text-white" }`}
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleInputKeyDown}
          disabled={isLoading}
          autoFocus
          ref={inputRef}
        />
        <Button
          className={`${currentTheme === "dark" ? "bg-[#E31F26] text-white" : "bg-white text-[#E31F26]"}`}
          type="submit"
          variant="default"
          size="default"
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? <Ellipsis className="animate-pulse" /> : <SendHorizontal />}
        </Button>
      </form>
    </div>
  );
}