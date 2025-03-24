import { useState, useRef, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { MessageSquare, Send, Loader2, PlusCircle } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface Message {
  role: "user" | "assistant";
  content: string;
  id: string;
}

interface ApiResponse {
  response?: string;
  context?: number[];
  error?: string;
}

const generateId = () => Math.random().toString(36).substr(2, 9);

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [context, setContext] = useState<number[]>([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const clearChat = () => {
    setMessages([]);
    setInput("");
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const trimmedInput = input.trim();
    if (!trimmedInput || loading) return;

    const userMessage: Message = {
      role: "user",
      content: trimmedInput,
      id: generateId(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:11434/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "llama3.1",
          prompt: trimmedInput,
          context: context,
        }),
      });

      if (!res.ok) throw new Error("Network response was not ok");
      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = "";
      let assistantMessageId = generateId();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "",
          id: assistantMessageId,
        },
      ]);

      while (true) {
        const { done, value } = await reader.read();
        const chunk = decoder.decode(value, { stream: true });

        if (done) {     
          break;
        }

        try {
          const parsed = JSON.parse(chunk) as ApiResponse;
          console.log(parsed);
          if (parsed.response) {
            fullResponse += parsed.response;
            setMessages((prev) =>
              prev.map((message) =>
                message.id === assistantMessageId
                  ? { ...message, content: fullResponse }
                  : message
              )
            );
          }else if (parsed.context) {
            setContext(parsed.context);
          }
        } catch (e) {
          console.error("Error parsing JSON chunk:", chunk);
        }
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I encountered an error while processing your request.",
          id: generateId(),
        },
      ]);
    }

    setLoading(false);
  };

  const MessageContent = ({ content }: { content: string }) => (
    <ReactMarkdown
      components={{
        p: ({ children }) => <p className="mb-2">{children}</p>,
        h1: ({ children }) => (
          <h1 className="text-2xl font-bold mb-4">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-xl font-bold mb-3">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-lg font-bold mb-2">{children}</h3>
        ),
        ul: ({ children }) => (
          <ul className="list-disc pl-6 mb-4">{children}</ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal pl-6 mb-4">{children}</ol>
        ),
        li: ({ children }) => <li className="mb-1">{children}</li>,
        code: ({ children }) => (
          <code className="px-1.5 py-0.5 rounded">{children}</code>
        ),
        pre: ({ children }) => (
          <pre className="bg-gray-600 text-white p-4 rounded-lg overflow-x-auto mb-4">
            {children}
          </pre>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );

  return (
    <div className=" max-w-6xl mx-auto h-[calc(100vh-12rem)] p-4 flex flex-col">
      <div className="mb-4 flex justify-end">
        <Button
          onClick={clearChat}
          variant="outline"
          className="flex items-center gap-2"
        >
          <PlusCircle className="h-4 w-4" />
          New Chat
        </Button>
      </div>
      <Card className="flex-1 flex flex-col overflow-y-scroll">
        <CardContent className="p-4 flex-1 flex flex-col gap-4">
          <div className="flex-1 overflow-y-auto space-y-4 pr-4">
            {messages.length === 0 ? (
              <div className="h-full flex items-center justify-center text-muted-foreground">
                <div className="text-center space-y-3">
                  <MessageSquare className="mx-auto h-12 w-12" />
                  <p>Start a conversation!</p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-3 ${
                        message.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted"
                      }`}
                    >
                      <MessageContent content={message.content} />
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              placeholder="Type a message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              className="flex-1"
            />
            <Button type="submit" disabled={loading} size="icon">
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
