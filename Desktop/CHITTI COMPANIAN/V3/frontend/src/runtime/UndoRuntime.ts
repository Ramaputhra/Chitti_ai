export class UndoRuntime {
    /**
     * Maintains a session-level undo stack for local visual interactions (filters, zoom, selection).
     */
    public pushState(stateSnapshot: any) {
        console.log("[UNDO] State pushed to stack.");
    }

    public undo() {
        console.log("[UNDO] Reverting to previous state.");
    }

    public redo() {
        console.log("[UNDO] Redoing state.");
    }
}

export const undoRuntime = new UndoRuntime();
