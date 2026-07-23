import React from 'react';
import styles from './ExecutiveDashboard.module.css';

export interface ExecutiveDashboardProps {
  title?: string;
  summarySection?: React.ReactNode;
  metricsSection?: React.ReactNode;
  timelineSection?: React.ReactNode;
  insightsSection?: React.ReactNode;
}

export const ExecutiveDashboard: React.FC<ExecutiveDashboardProps> = ({
  title = "Executive Productivity Overview",
  summarySection,
  metricsSection,
  timelineSection,
  insightsSection,
}) => {
  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <h1 className={styles.title}>{title}</h1>
      </header>
      
      <main className={styles.grid}>
        <section className={styles.summaryArea}>{summarySection}</section>
        <section className={styles.metricsArea}>{metricsSection}</section>
        <section className={styles.insightsArea}>{insightsSection}</section>
        <section className={styles.timelineArea}>{timelineSection}</section>
      </main>
    </div>
  );
};

export default ExecutiveDashboard;
