export interface Meeting {
  id: string;
  title: string;
  date: string;
  duration: string;
  attendees: string[];
  status: 'processing' | 'completed' | 'failed';
  summary?: string;
  actionItems?: ActionItem[];
  transcript?: string;
}

export interface ActionItem {
  id: string;
  task: string;
  assignee: string;
  dueDate?: string;
  status: 'pending' | 'in-progress' | 'completed';
}

export interface VoiceProfile {
  id: string;
  name: string;
  department: string;
  audioFile?: string;
  status: 'trained' | 'pending' | 'processing';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: string[];
}
