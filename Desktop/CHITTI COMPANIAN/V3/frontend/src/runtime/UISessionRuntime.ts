import { usePresentationStore } from "../store/presentationStore";

export class UISessionRuntime {
    constructor() {
        console.log("UISessionRuntime initialized.");
    }

    public registerSession(sessionData: any) {
        // Mutates the Vanilla store directly, bypassing React
        usePresentationStore.setState((state) => ({
            sessions: { ...state.sessions, [sessionData.session_id]: sessionData },
            activeSessionId: sessionData.session_id
        }));
    }
}
