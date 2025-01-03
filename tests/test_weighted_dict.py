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
        # Create a test dictionary with multiple entries
        node_input = WeightedDictInput()
        dict1 = node_input.create_weighted_dict("key1", "value1", 1.0)[0]
        dict2 = node_input.create_weighted_dict("key2", "value2", 2.0)[0]
        
        # Combine dictionaries
        node_concat = WeightedDictConcat()
        combined_dict = node_concat.concat_dicts(dict1, dict2)[0]
        
        # Test selection
        node_select = WeightedDictSelect()
        
        # Test 1: Basic key selection with simple format
        result = node_select.select_from_dict(combined_dict, "key1", "simple")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "value1")
        
        # Test 2: Basic key selection with weighted_text format
        result = node_select.select_from_dict(combined_dict, "key2", "weighted_text")
        self.assertEqual(result[0], "(value2:2.0)")
        
        # Test 3: Error handling for invalid key
        with self.assertRaises(ValueError) as context:
            node_select.select_from_dict(combined_dict, "nonexistent_key", "simple")
        self.assertTrue("not found in weighted dictionary" in str(context.exception))
        
        # Test 4: Empty key handling
        with self.assertRaises(ValueError) as context:
            node_select.select_from_dict(combined_dict, "", "simple")
        self.assertTrue("not found in weighted dictionary" in str(context.exception))
        
        # Test 5: Special characters in keys
        special_dict = node_input.create_weighted_dict("key-with-hyphens", "special_value", 1.0)[0]
        result = node_select.select_from_dict(special_dict, "key-with-hyphens", "simple")
        self.assertEqual(result[0], "special_value")
        
        # Test 6: Unicode characters in keys and values
        unicode_dict = node_input.create_weighted_dict("🔑", "值", 1.0)[0]
        result = node_select.select_from_dict(unicode_dict, "🔑", "simple")
        self.assertEqual(result[0], "值")

        # Test 7: Format handling with unicode
        result = node_select.select_from_dict(unicode_dict, "🔑", "weighted_text")
        self.assertEqual(result[0], "(值:1.0)")

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
        
        node_select_group = WeightedDictSelectGroup()

        # Test 1: Basic key selection
        formatted_output, selected_dict = node_select_group.select_group(
            reformatted_dict, False, "simple", "key1,key2"
        )
        self.assertEqual(len(selected_dict), 2)
        self.assertIn("key1", selected_dict)
        self.assertIn("key2", selected_dict)

        # Test 2: Various input formats
        test_cases = [
            ("key1, key2", ["key1", "key2"]),
            ("key1;key2", ["key1", "key2"]),
            ('  key1  ,  key2  ', ["key1", "key2"]),
            ('"key1",key2', ["key1", "key2"]),
            ('key1,,,key2', ["key1", "key2"]),
            ('key1;; ;  key2', ["key1", "key2"]),
        ]

        for input_str, expected_keys in test_cases:
            formatted_output, selected_dict = node_select_group.select_group(
                reformatted_dict, False, "simple", input_str
            )
            self.assertEqual(set(selected_dict.keys()), set(expected_keys))

        # Test 3: Duplicates handling
        formatted_output, selected_dict = node_select_group.select_group(
            reformatted_dict, True, "simple", "key1,key1,key1"
        )
        self.assertEqual(len(selected_dict), 3)  # Should have three entries with duplicates
        
        formatted_output, selected_dict = node_select_group.select_group(
            reformatted_dict, False, "simple", "key1,key1,key2"
        )
        self.assertEqual(len(selected_dict), 2)  # Should have two unique keys
        self.assertIn("key1", selected_dict)
        self.assertIn("key2", selected_dict)

        # Test 4: Error handling
        with self.assertRaises(ValueError) as context:
            node_select_group.select_group(
                reformatted_dict, False, "simple", "key1,invalid_key"
            )
        self.assertIn("Invalid key", str(context.exception))

        # Test 5: Empty input handling
        for empty_input in ["", None, "   ", ",,,", ";;;"]:
            with self.assertRaises(ValueError) as context:
                node_select_group.select_group(
                    reformatted_dict, False, "simple", empty_input
                )
            self.assertIn("Selected keys must be provided", str(context.exception))

    def test_parse_key_string(self):
        """Test the key string parsing functionality directly"""
        node = WeightedDictSelectGroup()
        
        test_cases = [
            ("key1,key2", ["key1", "key2"]),
            ("key1;key2", ["key1", "key2"]),
            ("  key1  ,  key2  ", ["key1", "key2"]),
            ('"key1",key2', ["key1", "key2"]),
            ("key1,,,key2", ["key1", "key2"]),
            ("key1;; ;  key2", ["key1", "key2"]),
            ("", []),
            (None, []),
            ("   ", []),
            (",,,", []),
            (";;;", []),
            ('"key1,with,comma",key2', ["key1,with,comma", "key2"]),
        ]

        for input_str, expected in test_cases:
            result = node._parse_key_string(input_str)
            self.assertEqual(result, expected, f"Failed for input: {input_str}")

    def test_weighted_dict_select_group_formatting(self):
        reformatted_dict = {
            "key1": {"value": "value1", "weight": 0.5},
            "key2": {"value": "value2", "weight": 0.3}
        }
        node_select_group = WeightedDictSelectGroup()

        # Test simple format
        formatted_output, selected_dict = node_select_group.select_group(
            reformatted_dict, False, "simple", "key1,key2"
        )
        self.assertEqual(formatted_output, "value1\nvalue2")

        # Test weighted_text format
        formatted_output, selected_dict = node_select_group.select_group(
            reformatted_dict, False, "weighted_text", "key1,key2"
        )
        self.assertEqual(formatted_output, "(value1:0.5)\n(value2:0.3)")

if __name__ == '__main__':
    unittest.main() 