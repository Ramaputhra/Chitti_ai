export class TypographyRuntime {
    /**
     * Manages fonts, sizes, spacing, and headings across all widgets.
     */
    public applyTypographySet(setId: string) {
        console.log(`[TYPOGRAPHY] Applying typography set: ${setId}`);
        // e.g. Setting CSS variables on :root
    }

    public getFontFamily(type: "sans" | "serif" | "mono"): string {
        return type === "mono" ? "monospace" : "sans-serif";
    }
}

export const typographyRuntime = new TypographyRuntime();
