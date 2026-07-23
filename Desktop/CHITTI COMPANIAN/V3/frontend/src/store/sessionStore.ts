import { createStore } from "zustand/vanilla";

export type ConnectionState = "DISCONNECTED" | "CONNECTED" | "HANDSHAKE" | "READY" | "ACTIVE" | "RECOVERING" | "CLOSED";

export interface SessionState {
  connectionState: ConnectionState;
  setConnectionState: (state: ConnectionState) => void;
}

export const useSessionStore = createStore<SessionState>((set) => ({
  connectionState: "DISCONNECTED",
  setConnectionState: (state) => set({ connectionState: state })
}));
