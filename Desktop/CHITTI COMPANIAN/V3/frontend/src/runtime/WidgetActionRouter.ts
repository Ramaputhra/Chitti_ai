import { WidgetAction } from "../templates/interfaces";

export class WidgetActionRouter {
    /**
     * Rule 328 & 330: Receives immutable actions, classifies them, 
     * and routes them to local state runtimes or up to the platform.
     * NEVER executes business logic directly.
     */
    public route(action: WidgetAction): void {
        console.log(`[ROUTER] Routing action: ${action.actionType} | Scope: ${action.scope}`);
        
        // 1. Classification & Validation
        // (Check Widget Locks, Interaction Policies here)
        
        // 2. Routing
        switch (action.scope) {
            case "LOCAL":
            case "SESSION":
                this.routeToLocalRuntimes(action);
                break;
            case "PLATFORM":
                this.promoteToPlatform(action);
                break;
            case "SYSTEM":
                console.log("[ROUTER] Handling system action (e.g., Close Session)");
                break;
        }

        // 3. Log Metrics
        // MetricsRuntime.record(action);
    }

    private routeToLocalRuntimes(action: WidgetAction) {
        // Delegate to specific State Runtimes based on actionType
        // e.g. if actionType == "SELECT", route to SelectionRuntime
        console.log(`[ROUTER] Delegating ${action.actionType} to local runtimes.`);
    }

    private promoteToPlatform(action: WidgetAction) {
        // Convert to FrontendEvent and emit via WebSocket via UIEventRuntime
        console.log(`[ROUTER] Promoting ${action.actionType} to platform execution.`);
    }
}

export const actionRouter = new WidgetActionRouter();
