import React from 'react';

interface ChartAdapterProps {
    dataset: any; // e.g. ChartDataset
    config: any;
    library?: "echarts" | "chartjs"; // Pluggable underlying engine
}

/**
 * Common ChartAdapter avoiding independent LineChart, BarChart logic.
 */
export const ChartAdapter: React.FC<ChartAdapterProps> = ({ dataset, config, library = "echarts" }) => {
    return (
        <div className="chart-adapter" style={{ width: '100%', height: '300px', backgroundColor: '#f9f9f9', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ color: '#888' }}>[Chart Rendered via {library}]</span>
        </div>
    );
};
