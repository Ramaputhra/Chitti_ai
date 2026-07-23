from desktop.models.composer import WorkflowBlueprint

class WorkflowValidator:
    """
    Rule 305: Every WorkflowBlueprint must pass structural validation before it reaches the Planner.
    Checks for cycles, missing inputs, and unavailable services.
    """
    
    def validate(self, blueprint: WorkflowBlueprint) -> bool:
        blueprint.validation_trace.clear()
        
        if not blueprint.nodes:
            blueprint.validation_trace.append("Blueprint contains no nodes.")
            blueprint.is_valid = False
            return False
            
        if self._has_cycles(blueprint):
            blueprint.validation_trace.append("Blueprint contains circular dependencies.")
            blueprint.is_valid = False
            return False
            
        if not self._validate_data_flow(blueprint):
            blueprint.is_valid = False
            return False
            
        blueprint.is_valid = True
        blueprint.validation_trace.append("Validation passed.")
        return True
        
    def _has_cycles(self, blueprint: WorkflowBlueprint) -> bool:
        # Stub: implement standard DFS cycle detection
        return False
        
    def _validate_data_flow(self, blueprint: WorkflowBlueprint) -> bool:
        # Stub: verify that for every node, its input_mapping maps to a valid output_mapping
        # from one of its dependencies or from the global intent inputs.
        return True
