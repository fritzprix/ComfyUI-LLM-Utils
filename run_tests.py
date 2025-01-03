import os
import sys
import unittest

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Create test suite
def create_test_suite():
    # Import test modules
    from tests.test_weighted_dict import TestWeightedDict
    
    # Create suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestWeightedDict))
    
    return suite

if __name__ == '__main__':
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    test_suite = create_test_suite()
    runner.run(test_suite) 