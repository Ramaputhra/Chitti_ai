import { widgetRegistry } from "./widgetRegistry";
import { layoutRegistry } from "./layoutRegistry";

class ThemeRegistry {
    // Stores themes (Medical, Minimal, Developer)
}
class SkinRegistry {
    // Stores skins (Glass, Material, Compact)
}
class AnimationRegistry {
    // Stores animation packs
}
class IconRegistry {
    // Stores icon sets
}

export class ComponentRegistry {
    /**
     * Unified Registry encapsulating all Presentation Components (Rule 338).
     */
    public widgets = widgetRegistry;
    public layouts = layoutRegistry;
    public themes = new ThemeRegistry();
    public skins = new SkinRegistry();
    public animations = new AnimationRegistry();
    public icons = new IconRegistry();

    public validateCompatibility() {
        // Rule 339: Component compatibility must be validated before registration
    }
}

export const componentRegistry = new ComponentRegistry();
