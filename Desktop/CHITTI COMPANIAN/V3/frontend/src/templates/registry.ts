import { IPresentationTemplate } from "./interfaces";

class TemplateRegistry {
    private templates: Record<string, new () => IPresentationTemplate> = {};

    register(id: string, templateClass: new () => IPresentationTemplate) {
        this.templates[id] = templateClass;
    }

    find(id: string): new () => IPresentationTemplate {
        if (!this.templates[id]) {
            throw new Error(`Template ${id} not found`);
        }
        return this.templates[id];
    }
}

export const registry = new TemplateRegistry();
