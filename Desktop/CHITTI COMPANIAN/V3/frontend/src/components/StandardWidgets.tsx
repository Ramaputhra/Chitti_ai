import React from 'react';

export const ErrorWidget: React.FC<{ message?: string }> = ({ message }) => {
    return (
        <div style={{ padding: '1rem', border: '1px solid red', color: 'red' }}>
            <h4>Widget Error</h4>
            <p>{message || "Failed to load widget."}</p>
        </div>
    );
};

export const LoadingWidget: React.FC = () => {
    return (
        <div style={{ padding: '1rem', color: 'gray', fontStyle: 'italic' }}>
            <p>Loading widget...</p>
        </div>
    );
};
