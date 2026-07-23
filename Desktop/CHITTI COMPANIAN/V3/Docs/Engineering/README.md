# CHITTI Engineering Documentation

This directory is the authoritative engineering reference for CHITTI V1.

Reading order:

1. CHITTI_V1_Integration_Audit_Report.md

2. CHITTI_V1_Integration_Master_Blueprint.md

3. antigravity_commands.md

4. CHITTI_V1_MASTER_ENGINEERING_SPECIFICATION
   Parts 1–10

Only after reading all documents may implementation begin.

These documents supersede implementation assumptions and earlier chat discussions where conflicts arise.

## Phase 3 Engineering Rule

ConversationRuntime is the sole gateway into the execution pipeline. 
PlannerRuntime shall receive only validated execution intents. 
Conversation intents never enter PlannerRuntime.