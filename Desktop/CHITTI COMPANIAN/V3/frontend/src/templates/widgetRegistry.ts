import { IWidget } from "./interfaces";

export interface WidgetDescriptor {
    widget_id: string;
    widget_version: string;
    widget_namespace: string;
}

class WidgetRegistry {
    private widgets: Record<string, new () => IWidget> = {};

    register(id: string, widgetClass: new () => IWidget) {
        this.widgets[id] = widgetClass;
    }

    resolve(id: string): new () => IWidget {
        if (!this.widgets[id]) {
            // Fallback to error widget
            console.warn(`Widget ${id} not found, falling back to System Error Widget.`);
            return this.widgets["core.system.error"];
        }
        return this.widgets[id];
    }
}

export const widgetRegistry = new WidgetRegistry();
