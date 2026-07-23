import React, { useEffect } from 'react';
import { useStore } from 'zustand';
import { usePresentationStore } from '../store/presentationStore';
import { registry } from '../templates/registry';
import { runtimeManager } from '../runtime/FrontendRuntimeManager';

export const PresentationHost: React.FC = () => {
    const activeSessionId = useStore(usePresentationStore, (state) => state.activeSessionId);
    const sessions = useStore(usePresentationStore, (state) => state.sessions);

    useEffect(() => {
        // Boot the runtime manager on mount
        runtimeManager.boot();
    }, []);

    if (!activeSessionId) {
        return (
            <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center' }}>
                <p>Waiting for active session...</p>
            </div>
        );
    }

    const session = sessions[activeSessionId];
    if (!session || !session.templateId) {
        return <p>Loading Template...</p>;
    }

    try {
        const TemplateClass = registry.find(session.templateId);
        // Normally we would instantiate this class or render it if it's a React wrapper
        return (
            <div>
                <h1>Rendered Template: {session.templateId}</h1>
                <pre>{JSON.stringify(session.model, null, 2)}</pre>
            </div>
        );
    } catch (e) {
        return <p>Template resolution failed: {String(e)}</p>;
    }
};
