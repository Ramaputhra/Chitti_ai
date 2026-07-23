import { usePresentationStore } from "../store/presentationStore";

export class UICommandRuntime {
    constructor() {
        console.log("UICommandRuntime initialized.");
    }

    public handleRenderCommand(command: any) {
        // E.g., patch state, spawn new session
        console.log("Handling render command for session: ", command.session_id);
    }
}
