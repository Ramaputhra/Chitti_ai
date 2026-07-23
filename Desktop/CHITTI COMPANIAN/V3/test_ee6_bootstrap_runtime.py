import unittest
from desktop.bootstrap.container import DependencyContainer, ServiceRegistry, ServiceDeclaration

class TestEE6Runtime(unittest.TestCase):
    def test_circular_dependency_rejection(self):
        reg = ServiceRegistry()
        cont = DependencyContainer(reg)
        
        decls = [
            ServiceDeclaration("A", ["A"], 1, 1) # Simple circle
        ]
        
        with self.assertRaises(ValueError):
            cont.validate_circular_dependencies(decls)
            
if __name__ == '__main__':
    unittest.main()
