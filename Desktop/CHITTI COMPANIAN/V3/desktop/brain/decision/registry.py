class DecisionPolicyRegistry:
    def __init__(self):
        self.safety_policies = []
        self.approval_policies = []
        
    def register_policy(self, category: str, policy: str):
        if category == "safety":
            self.safety_policies.append(policy)
        elif category == "approval":
            self.approval_policies.append(policy)
            
    def get_safety_policies(self):
        return self.safety_policies
