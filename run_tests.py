import os
import sys
import unittest

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Load and run tests
from nodes.test_weighted_dict import TestWeightedDict

if __name__ == '__main__':
    unittest.main(argv=[''], verbosity=2) 