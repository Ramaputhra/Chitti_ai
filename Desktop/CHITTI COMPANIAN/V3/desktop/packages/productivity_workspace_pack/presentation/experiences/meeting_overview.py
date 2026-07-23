from desktop.models.presentation import PresentationModel

class MeetingOverviewExperience:
    def present(self, data, mode: str) -> PresentationModel:
        """
        Renders the Meeting Companion dashboard dynamically based on the lifecycle mode.
        
        mode == "PREPARATION":
        - Meeting Timeline (shows current stage)
        - MeetingHealth Card
        - InsightCard (e.g., "Proposal changed since last meeting")
        - DocumentCards (Relevant files)
        
        mode == "LIVE":
        - Live Notes Field
        - Current Agenda Timer
        - Quick action to log a Decision / ActionItem
        
        mode == "POST_MEETING":
        - Extracted ActionItems
        - Draft Follow-up preview
        - Activity Goal updates
        """
        pass
