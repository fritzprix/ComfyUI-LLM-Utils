import unittest
import sys
import os

from nodes.weighted_dict import WeightedDictInput, WeightedDictSelect, WeightedDictConcat, WeightedDictSelectGroup

# Mock ComfyUI's dependencies if needed
try:
    import torch
except ImportError:
    pass

class TestWeightedDict(unittest.TestCase):
    def test_weighted_dict_input(self):
        # Test single entry creation
        node = WeightedDictInput()
        result = node.create_weighted_dict("test_key", "test_value", 2.5)
        
        self.assertEqual(len(result), 1)  # Should return a tuple with one item
        weighted_dict = result[0]
        
        # Check structure
        self.assertIn("items", weighted_dict)
        self.assertIn("weights", weighted_dict)
        
        # Check content
        self.assertEqual(weighted_dict["items"], {"test_key": "test_value"})
        self.assertEqual(weighted_dict["weights"], {"test_key": 2.5})

    def test_weighted_dict_concat(self):
        # Create test dictionaries
        node_input = WeightedDictInput()
        dict1 = node_input.create_weighted_dict("key1", "value1", 1.0)[0]
        dict2 = node_input.create_weighted_dict("key2", "value2", 2.0)[0]
        dict3 = node_input.create_weighted_dict("key3", "value3", 3.0)[0]
        
        # Test concatenation
        node_concat = WeightedDictConcat()
        
        # Test with two dictionaries
        result = node_concat.concat_dicts(dict1, dict2)
        self.assertEqual(len(result), 1)
        combined_dict = result[0]
        
        self.assertEqual(len(combined_dict["items"]), 2)
        self.assertEqual(combined_dict["items"]["key1"], "value1")
        self.assertEqual(combined_dict["items"]["key2"], "value2")
        self.assertEqual(combined_dict["weights"]["key1"], 1.0)
        self.assertEqual(combined_dict["weights"]["key2"], 2.0)
        
        # Test with three dictionaries
        result = node_concat.concat_dicts(dict1, dict2, dict3)
        combined_dict = result[0]
        
        self.assertEqual(len(combined_dict["items"]), 3)
        self.assertEqual(combined_dict["items"]["key3"], "value3")
        self.assertEqual(combined_dict["weights"]["key3"], 3.0)

    def test_weighted_dict_select(self):
        # Create a test dictionary with known values
        node_input = WeightedDictInput()
        dict1 = node_input.create_weighted_dict("key1", "value1", 1.0)[0]
        
        # Test selection
        node_select = WeightedDictSelect()
        result = node_select.select_from_dict(dict1)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "value1")  # With single entry, should always select this

    def test_weighted_dict_select_group(self):
        # Create test dictionaries and combine them
        node_input = WeightedDictInput()
        dict1 = node_input.create_weighted_dict("key1", "value1", 1.0)[0]
        dict2 = node_input.create_weighted_dict("key2", "value2", 2.0)[0]
        dict3 = node_input.create_weighted_dict("key3", "value3", 3.0)[0]
        
        node_concat = WeightedDictConcat()
        combined_dict = node_concat.concat_dicts(dict1, dict2, dict3)[0]
        
        # Convert to reformatted dict format
        reformatted_dict = {}
        for key in combined_dict["items"]:
            reformatted_dict[key] = {
                "value": combined_dict["items"][key],
                "weight": combined_dict["weights"][key]
            }
        
        # Test selection with duplicates allowed
        node_select_group = WeightedDictSelectGroup()
        formatted_output, selected_dict = node_select_group.select_group(
            reformatted_dict, 2, True
        )
        
        # Check output format
        self.assertIsInstance(formatted_output, str)
        self.assertIsInstance(selected_dict, dict)
        self.assertGreaterEqual(len(selected_dict), 1)
        
        # Test selection without duplicates
        formatted_output, selected_dict = node_select_group.select_group(
            reformatted_dict, 2, False
        )
        
        self.assertEqual(len(selected_dict), 2)
        # Verify all selected items are unique
        selected_values = [item["value"] for item in selected_dict.values()]
        self.assertEqual(len(selected_values), len(set(selected_values)))

if __name__ == '__main__':
    unittest.main() 