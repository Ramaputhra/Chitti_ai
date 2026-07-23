import { createStore } from "zustand/vanilla";

export interface PresentationState {
  // Add detailed model types later
  activeSessionId: string | null;
  sessions: Record<string, any>; // maps session_id to Session data
}

export const usePresentationStore = createStore<PresentationState>((set) => ({
  activeSessionId: null,
  sessions: {},
}));
