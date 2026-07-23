export type ActionScope = "LOCAL" | "SESSION" | "PLATFORM" | "SYSTEM";
export type ActionPriority = "LOW" | "NORMAL" | "HIGH" | "CRITICAL";
export type ActionOrigin = "USER" | "SYSTEM" | "NARRATION" | "SYNC" | "PLUGIN";

export interface WidgetAction {
    readonly actionId: string;
    readonly widgetId: string;
    readonly actionType: string;
    readonly scope: ActionScope;
    readonly priority: ActionPriority;
    readonly payload: unknown;
    readonly correlationId: string;
    readonly timestamp: number;
    readonly origin: ActionOrigin;
}

export interface WidgetInteractionPolicy {
    allowSelection: boolean;
    allowMultiSelection: boolean;
    allowExport: boolean;
    allowShare: boolean;
    allowContextMenu: boolean;
    allowDrag: boolean;
    allowResize: boolean;
}

export interface IWidget {
    initialize(): void;
    mount(): void;
    render(state: any, data: any): void;
    patch(patchData: any): void;
    suspend(): void;
    resume(): void;
    animate(animationId: string): void;
    dispose(): void;
}

export interface IPresentationTemplate {
    initialize(): void;
    render(model: any): void;
    patch(patch: any): void;
    suspend(): void;
    resume(): void;
    dispose(): void;
    supports(): string[];
}

export interface IAccessibilityRuntime {
    applyTheme(themeId: string): void;
    applyScale(scaleFactor: number): void;
    applyMotion(reducedMotion: boolean): void;
    announce(message: string): void;
    focus(widgetId: string): void;
    highContrast(enabled: boolean): void;
}

