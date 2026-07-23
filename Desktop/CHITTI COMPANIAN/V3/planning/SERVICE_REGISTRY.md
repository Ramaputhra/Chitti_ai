# CHITTI Service Registry & Dependency Graph

This document defines the application's core service topology, tracking the startup sequence and lifecycle ownership.

**Rule:** Every service must answer 4 questions: Who creates it? Who owns it? Who depends on it? Who destroys it?

## Startup Order

1. **ConfigurationService**
   - Created by: Application Bootstrap
   - Owned by: ApplicationContext
   - Used by: Everything
   - Destroyed by: LifecycleManager

2. **LoggingService**
   - Created by: Application Bootstrap
   - Owned by: ApplicationContext
   - Used by: Everything
   - Destroyed by: LifecycleManager

3. **VersionManager**
   - Created by: Application Bootstrap
   - Owned by: ApplicationContext
   - Used by: Logging, Health, UI, Telemetry
   - Destroyed by: LifecycleManager

4. **EventBus**
   - Created by: Application Bootstrap
   - Owned by: ApplicationContext
   - Used by: Most Subsystems (Pub/Sub)
   - Destroyed by: LifecycleManager

5. **LifecycleManager**
   - Created by: Application Bootstrap
   - Owned by: ApplicationContext
   - Used by: System shutdown hooks, Main application loop
   - Destroyed by: OS exit

6. **ThemeManager**
   - Created by: UI Subsystem
   - Owned by: ApplicationContext
   - Used by: UI Components
   - Destroyed by: LifecycleManager

7. **ApplicationContext**
   - Created by: Application Bootstrap
   - Owned by: Main process
   - Used by: Dependency Injection container
   - Destroyed by: LifecycleManager
