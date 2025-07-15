"use client";
import React, { useState, useRef, useEffect } from "react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { getInitialTheme } from "@/lib/utils";

interface Message {
  role: "user" | "assistant";
  content: string;
}

function getSessionId() {
  // Try to persist session_id in localStorage for the session
  if (typeof window === "undefined") return "";
  let sessionId = localStorage.getItem("airtel-chatbot-session-id");
  if (!sessionId) {
    sessionId = crypto.randomUUID();
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
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !sessionId) return;
    setHasError(null);
    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, session_id: sessionId }),
      });
      if (!res.ok) throw new Error("Failed to get response from server");
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.answer || data.response || "No response." },
      ]);
    } catch (err) {
      const error = err as Error;
      setHasError(error.message || "Unknown error");
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
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
      {/* Messages area */}
      <div
        className={
          "flex-1 w-full overflow-y-auto px-2 mb-2 space-y-2 airtel-chat-scrollbar"
        }
        aria-label="Chat messages"
        tabIndex={0}
        style={{ minHeight: 0 }}
      >
        {messages.length === 0 && (
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
              className={`rounded-lg px-4 py-2 max-w-[80%] break-words text-sm shadow-md ${
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
        {/* Loading spinner */}
        {isLoading && (
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
        <div className="w-full text-center text-xs text-red-600 mb-2">{hasError}</div>
      )}
      {/* Input area */}
      <form
        className="flex w-full gap-2 items-center"
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
      >
        <input
          type="text"
          className="flex-1 rounded-md px-3 py-2 text-base border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#E31F26] text-black"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleInputKeyDown}
          disabled={isLoading}
        />
        <Button
          type="submit"
          variant="default"
          size="default"
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? "..." : "Send"}
        </Button>
      </form>
    </div>
  );
}