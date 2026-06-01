import type { ChatResponse, DashboardSummary } from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function getDashboard(): Promise<DashboardSummary> {
  return request<DashboardSummary>("/dashboard");
}

export function askAssistant(question: string): Promise<ChatResponse> {
  return request<ChatResponse>("/assistant/chat", {
    method: "POST",
    body: JSON.stringify({ question })
  });
}
