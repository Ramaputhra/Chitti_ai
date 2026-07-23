# Architecture Freeze

Phase L (Knowledge) and Phase M (Goal-Oriented Cognition) are architecturally frozen. 

New architectural abstractions require explicit justification demonstrating that the existing contracts cannot express the required behavior. Preference shall always be given to extending existing implementations rather than introducing new architectural layers.

From this point onward, repository changes should be driven by product capabilities, not architectural ideas. Every new line of code must answer: *"Does this make CHITTI noticeably more useful to the user?"*
