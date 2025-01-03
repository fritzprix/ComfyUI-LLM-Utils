import unittest
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nodes.weighted_dict import (
    WeightedDictInput,
    WeightedDictSelect,
    WeightedDict,
    WeightedDictToPrompt,
    WeightedDictSelectGroup
)

class TestWeightedDict(unittest.TestCase):
    def setUp(self):
        # Create common test data
        self.input_node = WeightedDictInput()
        self.base_dict = self.input_node.create_weighted_dict(
            entry_count=3,
            key_1="cat", value_1="meow", weight_1=2.0,
            key_2="dog", value_2="woof", weight_2=1.0,
            key_3="bird", value_3="chirp", weight_3=1.0
        )[0]
        
        # Convert to reformatted dict
        self.formatter = WeightedDict()
        self.formatted_dict = self.formatter.reformat_dict(self.base_dict)[0]

    def test_weighted_dict_input(self):
        # Test dictionary creation
        self.assertEqual(self.base_dict["items"]["cat"], "meow")
        self.assertEqual(self.base_dict["weights"]["cat"], 2.0)
        self.assertEqual(len(self.base_dict["items"]), 3)
        
        # Test with minimum entries
        min_dict = self.input_node.create_weighted_dict(
            entry_count=1,
            key_1="test", value_1="value", weight_1=1.0
        )[0]
        self.assertEqual(len(min_dict["items"]), 1)

    def test_weighted_dict_format(self):
        # Test dictionary reformatting
        self.assertEqual(self.formatted_dict["cat"]["value"], "meow")
        self.assertEqual(self.formatted_dict["cat"]["weight"], 2.0)
        self.assertTrue(all(
            "value" in data and "weight" in data 
            for data in self.formatted_dict.values()
        ))

    def test_weighted_dict_select(self):
        # Test single selection
        selector = WeightedDictSelect()
        result = selector.select_from_dict(self.base_dict)[0]
        self.assertIn(result, ["meow", "woof", "chirp"])
        
        # Test distribution (basic)
        selections = [
            selector.select_from_dict(self.base_dict)[0] 
            for _ in range(1000)
        ]
        meow_count = selections.count("meow")
        self.assertGreater(meow_count, 200)  # Should appear more due to higher weight

    def test_weighted_dict_to_prompt(self):
        prompt_node = WeightedDictToPrompt()
        
        # Test basic template
        template = "The {{ cat }} and {{ dog }}"
        result = prompt_node.render_prompt(template, self.formatted_dict)[0]
        self.assertEqual(result, "The meow and woof")
        
        # Test missing placeholder
        template = "The {{ missing }}"
        result = prompt_node.render_prompt(template, self.formatted_dict)[0]
        self.assertEqual(result, "The {{ missing }}")

    def test_weighted_dict_select_group(self):
        group_selector = WeightedDictSelectGroup()
        
        # Test without duplicates
        formatted_str, selected_dict = group_selector.select_group(
            self.formatted_dict,
            count=2,
            allow_duplicates=False
        )
        
        # Check formatted string format
        self.assertTrue(":" in formatted_str)
        self.assertEqual(formatted_str.count(","), 1)  # Two items = one comma
        
        # Check selected dictionary
        self.assertEqual(len(selected_dict), 2)
        self.assertTrue(all(
            "value" in data and "weight" in data 
            for data in selected_dict.values()
        ))
        
        # Test with duplicates
        formatted_str, selected_dict = group_selector.select_group(
            self.formatted_dict,
            count=4,
            allow_duplicates=True
        )
        self.assertEqual(formatted_str.count(","), 3)  # Four items = three commas
        
        # Test requesting more items than available (without duplicates)
        formatted_str, selected_dict = group_selector.select_group(
            self.formatted_dict,
            count=5,
            allow_duplicates=False
        )
        self.assertEqual(len(selected_dict), 3)  # Should only return available items

if __name__ == '__main__':
    unittest.main() 