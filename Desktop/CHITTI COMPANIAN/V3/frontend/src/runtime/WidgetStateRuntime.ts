import { usePresentationStore } from "../store/presentationStore";

export class WidgetStateRuntime {
    /**
     * Stores generic state for any widget (e.g., expanded, selectedRow, zoomLevel).
     * Rule 327: Widgets do not own state.
     */
    public setWidgetState(widgetId: string, key: string, value: any) {
        console.log(`[STATE] Updating ${widgetId} -> ${key} = ${value}`);
        // Mutates Zustand store
        // usePresentationStore.setState(...)
    }

    public getWidgetState(widgetId: string, key: string): any {
        // Reads from Zustand store
        return null;
    }
}

export const widgetStateRuntime = new WidgetStateRuntime();
