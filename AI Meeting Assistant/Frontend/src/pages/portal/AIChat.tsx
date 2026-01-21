import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, FileText, Loader2 } from 'lucide-react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ChatMessage } from '@/types/meeting';
import { format } from 'date-fns';
import { sendToRAG } from "@/api";

const suggestedQuestions = [
  "What was decided about the Q4 roadmap?",
  "Who is assigned to the mobile redesign?",
  "Summarize last week's meetings",
  "What are the pending action items?",
];

const AIChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  useEffect(scrollToBottom, [messages]);

  const handleSend = async (query: string = input) => {
    if (!query.trim()) return;

    const userMessage: ChatMessage = {
      id: `u${Date.now()}`,
      role: 'user',
      content: query.trim(),
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendToRAG(query);
      const assistantMessage: ChatMessage = {
        id: `a${Date.now()}`,
        role: 'assistant',
        content: response,
        timestamp: new Date(),
        sources: [], // optional: you can add sources from backend if available
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Error contacting RAG backend:", err);
      const errorMessage: ChatMessage = {
        id: `a${Date.now()}`,
        role: 'assistant',
        content: "Sorry, I couldn't reach the backend.",
        timestamp: new Date(),
        sources: [],
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <DashboardLayout>
      <div className="h-[calc(100vh-5rem)] flex flex-col max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-primary shadow-glow">
            <Bot className="h-6 w-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-foreground">AI Meeting Assistant</h1>
            <p className="text-muted-foreground">Ask questions about past meetings and action items</p>
          </div>
        </div>

        {/* Chat Container */}
        <Card className="flex-1 flex flex-col overflow-hidden">
          <ScrollArea className="flex-1 p-6">
            <div className="space-y-6">
              {messages.map(message => (
                <div
                  key={message.id}
                  className={`flex gap-4 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
                >
                  <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${
                    message.role === 'assistant' ? 'bg-gradient-primary' : 'bg-secondary'
                  }`}>
                    {message.role === 'assistant' ? <Bot className="h-5 w-5 text-primary-foreground" /> : <User className="h-5 w-5 text-secondary-foreground" />}
                  </div>
                  <div className={`flex-1 max-w-[80%] ${message.role === 'user' ? 'text-right' : ''}`}>
                    <div className={`inline-block rounded-2xl px-4 py-3 ${
                      message.role === 'assistant' ? 'bg-muted text-foreground' : 'bg-primary text-primary-foreground'
                    }`}>
                      <p className="text-sm whitespace-pre-wrap text-left">{message.content}</p>
                    </div>
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        {message.sources.map((source, i) => (
                          <span key={i} className="inline-flex items-center gap-1.5 rounded-full bg-accent px-2.5 py-1 text-xs text-accent-foreground">
                            <FileText className="h-3 w-3" />
                            {source}
                          </span>
                        ))}
                      </div>
                    )}
                    <p className="mt-1 text-xs text-muted-foreground">{format(message.timestamp, 'h:mm a')}</p>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-primary">
                    <Bot className="h-5 w-5 text-primary-foreground" />
                  </div>
                  <div className="flex items-center gap-2 rounded-2xl bg-muted px-4 py-3">
                    <Loader2 className="h-4 w-4 animate-spin text-primary" />
                    <span className="text-sm text-muted-foreground">Thinking...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* Suggested Questions */}
          {messages.length <= 1 && (
            <div className="border-t border-border px-6 py-4">
              <p className="text-xs font-medium text-muted-foreground mb-3 flex items-center gap-1.5">
                <Sparkles className="h-3.5 w-3.5" />
                Suggested questions
              </p>
              <div className="flex flex-wrap gap-2">
                {suggestedQuestions.map((question, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(question)}
                    className="rounded-full bg-accent px-3 py-1.5 text-sm text-accent-foreground hover:bg-primary hover:text-primary-foreground transition-colors"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="border-t border-border p-4 flex items-center gap-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about meetings, decisions, or action items..."
              className="h-12"
              disabled={isLoading}
            />
            <Button
              onClick={() => handleSend()}
              disabled={!input.trim() || isLoading}
              className="h-12 w-12 shrink-0"
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default AIChat;
