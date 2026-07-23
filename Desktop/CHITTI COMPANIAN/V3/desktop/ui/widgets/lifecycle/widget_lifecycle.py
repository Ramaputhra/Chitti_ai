import logging
from desktop.ui.widgets.sdk.widget import BaseWidget
from desktop.ui.widgets.lifecycle.widget_state_machine import WidgetStateMachine, WidgetLifecycleState

logger = logging.getLogger(__name__)

class WidgetLifecycleManager:
    """
    S36D-2: Manages Widget Lifecycle transitions.
    """
    def __init__(self, widget: BaseWidget):
        self.widget = widget
        self.state_machine = WidgetStateMachine()

    def load(self):
        self.state_machine.transition_to(WidgetLifecycleState.LOADED)

    def bind(self):
        self.state_machine.transition_to(WidgetLifecycleState.BOUND)

    def attach(self):
        self.state_machine.transition_to(WidgetLifecycleState.ATTACHED)

    def destroy(self):
        self.state_machine.transition_to(WidgetLifecycleState.DESTROYED)
