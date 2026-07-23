class SystemEvents:
    """
    Standardized event IDs matching the EVENT_CATALOG.md namespaces.
    """
    APP_STARTING = "Application.Starting"
    APP_STARTED = "Application.Started"
    APP_STOPPING = "Application.Stopping"
    
    CONFIG_LOADED = "Configuration.Loaded"
    CONFIG_CHANGED = "Configuration.Changed"
    
    MODEL_NOT_INSTALLED = "Model.NotInstalled"
    
    SETTINGS_CHANGED = "Settings.Changed"
    
    STATE_CHANGED = "State.Changed"
    
    THEME_CHANGED = "Theme.Changed"
    
    VOICE_DEVICE_CHANGED = "Voice.DeviceChanged"
    VOICE_CAPTURE_STARTED = "Voice.CaptureStarted"
    VOICE_CAPTURE_STOPPED = "Voice.CaptureStopped"
    VOICE_AUDIO_FRAME = "Voice.AudioFrame"
    VOICE_SPEECH_STARTED = "Voice.SpeechStarted"
    VOICE_SPEECH_ENDED = "Voice.SpeechEnded"
    VOICE_AUDIO_READY = "Voice.AudioReady"
    VOICE_PLAYBACK_STARTED = "Voice.PlaybackStarted"
    VOICE_PLAYBACK_FINISHED = "Voice.PlaybackFinished"
    VOICE_ERROR = "Voice.Error"
    VOICE_SPEAKER_VERIFIED = "Voice.SpeakerVerified"
    
    LANGUAGE_TEXT_RECOGNIZED = "Language.TextRecognized"
    LANGUAGE_PROCESSING_STARTED = "Language.ProcessingStarted"
    LANGUAGE_PROCESSING_FINISHED = "Language.ProcessingFinished"
    ENTITY_EXTRACTION_COMPLETED = "EntityExtraction.Completed"
    
    OBSERVATIONS_RESOLVED = "Observation.Resolved"
    OBSERVATION_HISTORY_UPDATED = "Observation.HistoryUpdated"
    WORLD_STATE_UPDATED = "Observation.WorldStateUpdated"
    
    ACTIVITY_SESSION_STARTED = "Activity.SessionStarted"
    ACTIVITY_SESSION_UPDATED = "Activity.SessionUpdated"
    ACTIVITY_SESSION_ENDED = "Activity.SessionEnded"
    
    PROJECT_ACTIVATED = "Project.Activated"
    PROJECT_COMPLETED = "Project.Completed"
    PROJECT_AMBIGUOUS = "Project.Ambiguous"
    
    GOAL_STARTED = "Goal.Started"
    GOAL_PROGRESS_UPDATED = "Goal.ProgressUpdated"
    GOAL_PAUSED = "Goal.Paused"
    GOAL_COMPLETED = "Goal.Completed"
    
    WORKSPACE_UNMAPPED = "Workspace.Unmapped"
    
    ENTITY_CREATED = "Entity.Created"
    ENTITY_UPDATED = "Entity.Updated"
    FACT_STORED = "Fact.Stored"
    FACT_CONFLICT = "Fact.Conflict"
    MEMORY_CREATED = "Memory.Created"
    MEMORY_UPDATED = "Memory.Updated"
    
    INTENT_DETECTED = "Intent.Detected"
    INTENT_IGNORED = "Intent.Ignored"
    
    WORKFLOW_CREATED = "Workflow.Created"
    WORKFLOW_STARTED = "Workflow.Started"
    WORKFLOW_COMPLETED = "Workflow.Completed"
    WORKFLOW_FAILED = "Workflow.Failed"
    WORKFLOW_ROLLED_BACK = "Workflow.RolledBack"
    WORKFLOW_APPROVAL_REQUIRED = "Workflow.ApprovalRequired"
    WORKFLOW_APPROVAL_GRANTED = "Workflow.ApprovalGranted"
    WORKFLOW_APPROVAL_DENIED = "Workflow.ApprovalDenied"
    
    RESPONSE_GENERATED = "Response.Generated"
    
    MEMORY_STORED = "Memory.Stored"
    
    PLANNER_STATE_CHANGED = "Planner.StateChanged"   # payload: {"state": "Planning"|"Idle"}
    
    STEP_STARTED = "Workflow.StepStarted"              # payload: {"workflow_id", "step_id", "action"}
    STEP_COMPLETED = "Workflow.StepCompleted"          # payload: {"workflow_id", "step_id", "action", "result"}
    STEP_FAILED = "Workflow.StepFailed"                # payload: {"workflow_id", "step_id", "action", "error"}
    
    WORKFLOW_STEP_COMPLETED = "Workflow.LegacyStepCompleted" # Deprecated
    TASK_CREATED = "Task.Created"                      # payload: {"goal", "source_intent", "correlation_id"}
    TASK_STARTED = "Task.Started"                      # payload: {"task_context"}
    TASK_STATE_CHANGED = "Task.StateChanged"
    TASK_PROGRESS_UPDATED = "Task.ProgressUpdated"     # payload: {"task_id", "workflow_id", "step_name", "percent", "status_message", "timestamp"}
    TASK_CHECKPOINT_CREATED = "Task.CheckpointCreated"
    TASK_RECOVERED = "Task.Recovered"
    TASK_COMPLETED = "Task.Completed"
    TASK_PARAMETERS_REQUIRED = "Task.ParametersRequired" # payload: {"task_id", "missing_parameters": List[str]}
    
    HARDWARE_CONNECTED = "Hardware.Connected"

    FRAME_CAPTURED = "Perception.FrameCaptured"
    SCENE_UPDATED = "Perception.SceneUpdated"
    DESKTOP_UPDATED = "Perception.DesktopUpdated"
    ATTENTION_UPDATED = "Perception.AttentionUpdated"
    CONTEXT_UPDATED = "Context.Updated"

    # Productivity & Reflection Events
    PRODUCTIVITY_UPDATED = "Productivity.Updated"
    FOCUS_BLOCK_COMPLETED = "Productivity.FocusBlockCompleted"
    REFLECTION_GENERATED = "Reflection.Generated"
    DAILY_SUMMARY_READY = "Reflection.DailySummaryReady"
    WEEKLY_SUMMARY_READY = "Reflection.WeeklySummaryReady"
    
    # Prediction & Recommendation Runtime
    PREDICTION_MADE = "Prediction.Made"
    RECOMMENDATION_GENERATED = "Recommendation.Generated"
