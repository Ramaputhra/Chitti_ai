# CHITTI Platform Architecture v3.0

This document defines the frozen foundational architecture of the CHITTI Companion platform. The subsystems listed below have reached architectural maturity and stability.

## Core Subsystems

1. **Runtime Kernel**: The execution engine that processes immutable workflows safely and deterministically.
2. **Planner**: The cognitive component that translates user intent into template selection, parameter extraction, and goal creation.
3. **Scheduler**: The queue-based gateway that handles concurrency, priority, and admission control.
4. **Memory Runtime**: Manages all conversational state, episodic records, and long-term semantic knowledge via the MemoryAPI.
5. **Capability Runtime**: The execution layer where all product features (e.g., File Search, Calendar, Browser) are implemented as isolated, stateless capabilities.
6. **Template Runtime**: The declarative engine that compiles, caches, and instantiates reusable task workflows (Rules 71-75).
7. **Expression Runtime**: Manages avatar intent, emotion, and visual/audio expression independently of cognition.
8. **Semantic Runtime**: Processes background observations to extract facts and build knowledge graphs.
9. **Developer Console**: The observability layer for inspecting events, workflows, tasks, and memory.
10. **Event Bus**: The primary communication backbone ensuring loose coupling and deep inspectability (Rule 48).
11. **Dependency Injection**: The inversion of control container binding all services, models, and providers.
12. **Presence Runtime**: Manages CHITTI's operational modes (Active, Quiet, Sleep) and embodiment visibility states decoupled from execution.
13. **Activity Runtime**: Centralized event publisher tracking user, system, and app events continuously in the background.
14. **Lifecycle Manager**: Orchestrates deterministic graceful shutdown pipelines and system tray states.
15. **Window Manager**: Abstracts UI rendering logic to preserve interaction context during Presence transitions.

## Engineering Constitution

> These subsystems are considered architecturally frozen. Future changes must preserve their public interfaces unless a documented architectural review approves a platform version increment.
