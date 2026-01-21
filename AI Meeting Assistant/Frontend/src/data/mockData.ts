import { Meeting, VoiceProfile, ChatMessage } from '@/types/meeting';

export const mockMeetings: Meeting[] = [
  {
    id: '1',
    title: 'Q4 Product Roadmap Review',
    date: '2024-01-15T10:00:00',
    duration: '45 min',
    attendees: ['Alex Thompson', 'Jordan Rivera', 'Sam Chen', 'Taylor Kim'],
    status: 'completed',
    summary: 'Discussed Q4 product priorities including mobile app redesign, API v3 launch, and customer feedback integration. Agreed on timeline for mobile redesign completion by March. API v3 to enter beta in February.',
    actionItems: [
      { id: '1a', task: 'Create mobile redesign mockups', assignee: 'Taylor Kim', dueDate: '2024-01-22', status: 'in-progress' },
      { id: '1b', task: 'Draft API v3 documentation', assignee: 'Sam Chen', dueDate: '2024-01-25', status: 'pending' },
      { id: '1c', task: 'Schedule customer feedback sessions', assignee: 'Jordan Rivera', dueDate: '2024-01-18', status: 'completed' },
    ],
    transcript: 'Alex: Good morning everyone. Let\'s dive into our Q4 roadmap...',
  },
  {
    id: '2',
    title: 'Engineering Sprint Planning',
    date: '2024-01-14T14:00:00',
    duration: '60 min',
    attendees: ['Sam Chen', 'Morgan Lee', 'Casey Parker'],
    status: 'completed',
    summary: 'Sprint 23 planning completed. Focus areas: performance optimization, security patches, and new dashboard widgets. Team capacity at 85% due to planned PTO.',
    actionItems: [
      { id: '2a', task: 'Implement Redis caching layer', assignee: 'Morgan Lee', dueDate: '2024-01-28', status: 'pending' },
      { id: '2b', task: 'Security audit for auth module', assignee: 'Casey Parker', dueDate: '2024-01-21', status: 'in-progress' },
    ],
  },
  {
    id: '3',
    title: 'Client Onboarding - Acme Corp',
    date: '2024-01-13T09:30:00',
    duration: '30 min',
    attendees: ['Jordan Rivera', 'Client: John Smith', 'Client: Lisa Wang'],
    status: 'completed',
    summary: 'Completed initial onboarding call with Acme Corp. They require custom SSO integration and data migration from legacy system. Timeline: 6 weeks for full deployment.',
    actionItems: [
      { id: '3a', task: 'Send SOW for custom SSO', assignee: 'Jordan Rivera', dueDate: '2024-01-15', status: 'completed' },
      { id: '3b', task: 'Schedule technical deep-dive', assignee: 'Jordan Rivera', dueDate: '2024-01-17', status: 'pending' },
    ],
  },
  {
    id: '4',
    title: 'Weekly Design Sync',
    date: '2024-01-12T11:00:00',
    duration: '25 min',
    attendees: ['Taylor Kim', 'Alex Thompson'],
    status: 'completed',
    summary: 'Reviewed new component library updates. Discussed accessibility improvements for color contrast. Finalized icon set for v2 release.',
  },
  {
    id: '5',
    title: 'Budget Review Meeting',
    date: '2024-01-11T15:00:00',
    duration: '50 min',
    attendees: ['Alex Thompson', 'Finance Team'],
    status: 'processing',
  },
];

export const mockVoiceProfiles: VoiceProfile[] = [
  { id: 'v1', name: 'Alex Thompson', department: 'Leadership', status: 'trained' },
  { id: 'v2', name: 'Jordan Rivera', department: 'Sales', status: 'trained' },
  { id: 'v3', name: 'Sam Chen', department: 'Engineering', status: 'trained' },
  { id: 'v4', name: 'Taylor Kim', department: 'Design', status: 'pending' },
  { id: 'v5', name: 'Morgan Lee', department: 'Engineering', status: 'processing' },
];

export const mockChatHistory: ChatMessage[] = [
  {
    id: 'c1',
    role: 'assistant',
    content: 'Hello! I\'m your AI Meeting Assistant. I can help you find information from past meetings, summarize discussions, and track action items. What would you like to know?',
    timestamp: new Date(),
  },
];
