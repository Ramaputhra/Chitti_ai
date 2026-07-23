import { IPresentationTemplate } from "./interfaces";

export interface LayoutDescriptor {
    id: string;
    columns: number;
    rows: number;
}

class LayoutRegistry {
    private layouts: Record<string, new () => IPresentationTemplate> = {};

    register(id: string, layoutClass: new () => IPresentationTemplate) {
        this.layouts[id] = layoutClass;
    }

    resolve(id: string): new () => IPresentationTemplate {
        if (!this.layouts[id]) {
            throw new Error(`Layout ${id} not found`);
        }
        return this.layouts[id];
    }
}

export const layoutRegistry = new LayoutRegistry();
