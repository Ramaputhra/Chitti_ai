import { widgetStateRuntime } from "./WidgetStateRuntime";
import { selectionRuntime } from "./SelectionRuntime";
import { filterRuntime } from "./FilterRuntime";
import { highlightRuntime } from "./HighlightRuntime";
import { undoRuntime } from "./UndoRuntime";
import { actionRouter } from "./WidgetActionRouter";

export class FrontendRuntimeManager {
    // Platform Runtimes
    public widgetState = widgetStateRuntime;
    public selection = selectionRuntime;
    public filter = filterRuntime;
    public highlight = highlightRuntime;
    public undo = undoRuntime;
    public router = actionRouter;

    constructor() {
        console.log("FrontendRuntimeManager initialized with Interaction Runtimes.");
    }

    boot() {
        console.log("BOOT -> LOAD CONFIG -> LOAD THEME -> CONNECT -> HANDSHAKE...");
    }
}

export const runtimeManager = new FrontendRuntimeManager();
