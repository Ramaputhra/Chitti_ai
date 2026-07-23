export class ResponsiveRuntime {
    /**
     * Centralized runtime for breakpoint management.
     * desktop, tablet, mobile, compact, fullscreen.
     */
    public getCurrentBreakpoint(): string {
        const width = window.innerWidth;
        if (width < 768) return "mobile";
        if (width < 1024) return "tablet";
        return "desktop";
    }

    public isFullscreen(): boolean {
        return !!document.fullscreenElement;
    }
}

export const responsiveRuntime = new ResponsiveRuntime();
