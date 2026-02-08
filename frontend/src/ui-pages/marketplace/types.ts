export interface Employee {
  id: string;
  name: string;
  description: string;
  category: string[];
  tags: string[];
  price: number;
  originalPrice?: number; // Added to support the strikethrough price in screenshot
  trialCount: number;
  hireCount: number;
  avatar?: string;
  isHot?: boolean; // Optional: to visually match UI cues
  isRecruited?: boolean; // New field to track recruitment status
  isHired?:boolean;
}

export interface Category {
  id: string;
  name: string;
  count?: number;
}

export interface Message {
  id: string;
  role: 'user' | 'model';
  content: string;
  timestamp: number;
}

export interface ChatSession {
  id: string;
  title: string;
  employeeId: string;
  lastModified: number;
}