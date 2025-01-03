import random
from typing import Dict, Any

class WeightedDictInput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "key": ("STRING", {"default": "key1"}),
                "value": ("STRING", {"default": "value1"}),
                "weight": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 100.0}),
            }
        }
    
    RETURN_TYPES = ("DICT",)
    FUNCTION = "create_weighted_dict"
    CATEGORY = "llm-utils"

    def create_weighted_dict(self, key, value, weight) -> tuple[Dict[str, Any]]:
        # Create the weighted dictionary
        weighted_dict = {
            "items": {key: value},
            "weights": {key: float(weight)}
        }

        return (weighted_dict,)

class WeightedDictSelect:
    @classmethod
    def INPUT_TYPES(cls):
        """Define the input parameters for the node.
        
        Returns:
            dict: Configuration for input parameters:
                - weighted_dict: Dictionary containing weighted items
                - key: Key to select from the dictionary
                - output_format: Format option for the output (simple or weighted_text)
        """
        return {
            "required": {
                "weighted_dict": ("DICT",),
                "key": ("STRING", {"default": ""}),
                "output_format": (["simple", "weighted_text"], {"default": "simple"}),
            },
        }
    
    RETURN_TYPES = ("STRING", )  # Output will be a string
    FUNCTION = "select_from_dict"  # Main function to execute
    CATEGORY = "llm-utils"  # Node category in UI

    def _format_value(self, key: str, value: str, weight: float, format_type: str) -> str:
        """Format a value based on the specified format type.
        
        Args:
            key: The dictionary key
            value: The value to format
            weight: The weight associated with the value
            format_type: The desired output format ('simple' or 'weighted_text')
            
        Returns:
            str: Formatted string based on format_type:
                - simple: just the value
                - weighted_text: (value:weight)
        """
        if format_type == "simple":
            return value
        elif format_type == "weighted_text":
            return f"({value}:{weight})"
        return value  # fallback to simple

    def select_from_dict(self, weighted_dict: Dict[str, Any], key: str, output_format: str = "simple") -> tuple[str]:
        """Select and format a value from the weighted dictionary.
        
        Args:
            weighted_dict: Dictionary containing 'items' and 'weights' subdictionaries
            key: Key to select from the dictionary
            output_format: Desired output format ('simple' or 'weighted_text')
            
        Returns:
            tuple[str]: Single-element tuple containing the formatted value
            
        Raises:
            ValueError: If key is not found in the dictionary
        """
        # Extract items and weights from the dictionary
        items = weighted_dict.get("items", {})
        weights = weighted_dict.get("weights", {})
        
        # Validate key exists
        if key not in items:
            raise ValueError(f"Key '{key}' not found in weighted dictionary")
            
        # Get value and weight for the key
        value = items[key]
        weight = weights[key]
        
        # Format and return the value
        formatted_value = self._format_value(key, value, weight, output_format)
        return (formatted_value,)

class WeightedDict:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "weighted_dict": ("DICT",),
            },
        }
    
    RETURN_TYPES = ("DICT",)
    FUNCTION = "reformat_dict"
    CATEGORY = "llm-utils"

    def reformat_dict(self, weighted_dict: Dict[str, Any]) -> tuple[Dict[str, Any]]:
        items = weighted_dict["items"]
        weights = weighted_dict["weights"]
        
        # Create new format: Key: {value: v, weight: w}
        reformatted_dict = {}
        for key in items.keys():
            reformatted_dict[key] = {
                "value": items[key],
                "weight": weights[key]
            }
        
        return (reformatted_dict,)

class WeightedDictToPrompt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "template": ("STRING", {
                    "multiline": True, 
                    "default": "A {{ animal }} that says {{ sound }}"
                }),
                "weighted_dict": ("DICT",),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "render_prompt"
    CATEGORY = "llm-utils"

    def render_prompt(self, template: str, weighted_dict: Dict[str, Any]) -> tuple[str]:
        # Start with the template
        rendered = template
        
        # Check dictionary format and handle accordingly
        if "items" in weighted_dict:
            # Handle raw format
            items = weighted_dict["items"]
            for key, value in items.items():
                # Try both with and without spaces
                placeholders = [
                    f"{{{{ {key} }}}}",  # with spaces
                    f"{{{{{key}}}}}"      # without spaces
                ]
                for placeholder in placeholders:
                    if placeholder in rendered:
                        rendered = rendered.replace(placeholder, str(value))
        else:
            # Handle reformatted format
            for key, data in weighted_dict.items():
                placeholders = [
                    f"{{{{ {key} }}}}",  # with spaces
                    f"{{{{{key}}}}}"      # without spaces
                ]
                value = data["value"] if isinstance(data, dict) and "value" in data else str(data)
                for placeholder in placeholders:
                    if placeholder in rendered:
                        rendered = rendered.replace(placeholder, str(value))
            
        return (rendered,)

class WeightedDictSelectGroup:
    RETURN_TYPES = ("STRING", "DICT")
    FUNCTION = "select_group"
    CATEGORY = "llm-utils"

    @classmethod
    def INPUT_TYPES(cls):
        """Define the input parameters for the node.
        
        Returns:
            dict: Configuration for input parameters:
                - weighted_dict: Dictionary containing weighted items
                - allow_duplicates: Whether to allow duplicate selections
                - output_format: Format option for the output
                - selected_keys: String of keys to select
        """
        return {
            "required": {
                "weighted_dict": ("DICT",),
                "allow_duplicates": ("BOOLEAN", {"default": False}),
                "output_format": (["simple", "weighted_text"], {"default": "simple"}),
                "selected_keys": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "key1,key2,key3"
                }),
            }
        }
    
    def _parse_key_string(self, key_string):
        """Parse a string of keys into a list.
        
        Args:
            key_string: String containing comma or semicolon separated keys
            
        Returns:
            list: List of parsed keys
        """
        if not key_string or not isinstance(key_string, str):
            return []
            
        # Split by both comma and semicolon
        keys = []
        current_key = []
        in_quotes = False
        
        for char in key_string:
            if char == '"':
                in_quotes = not in_quotes
            elif char in ',;' and not in_quotes:
                if current_key:
                    keys.append(''.join(current_key).strip())
                    current_key = []
            else:
                current_key.append(char)
                
        if current_key:
            keys.append(''.join(current_key).strip())
            
        # Filter out empty strings and strip whitespace
        return [k.strip('"') for k in keys if k.strip()]

    def select_group(self, weighted_dict, allow_duplicates=False, output_format="simple", selected_keys=""):
        """Select a group of items from the weighted dictionary.
        
        Args:
            weighted_dict: Dictionary containing weighted items
            allow_duplicates: Whether to allow duplicate selections
            output_format: Desired output format ('simple' or 'weighted_text')
            selected_keys: String of specific keys to select
            
        Returns:
            tuple: (formatted_output, selected_dict)
                - formatted_output: String of formatted selections
                - selected_dict: Dictionary of selected items
        """
        if not selected_keys or selected_keys.strip() == "" or all(c in ",; " for c in selected_keys):
            raise ValueError("Selected keys must be provided")
            
        # Parse and validate specific keys
        parsed_keys = self._parse_key_string(selected_keys)
        invalid_keys = [k for k in parsed_keys if k not in weighted_dict]
        if invalid_keys:
            raise ValueError(f"Invalid key(s) found in selection: {', '.join(invalid_keys)}")
        
        # Handle duplicates
        if not allow_duplicates:
            seen = set()
            parsed_keys = [k for k in parsed_keys if not (k in seen or seen.add(k))]

        # Create selected dictionary maintaining order
        selected_dict = {}
        for i, key in enumerate(parsed_keys):
            # For duplicates, create unique keys by appending an index
            if allow_duplicates and key in selected_dict:
                new_key = f"{key}_{i}"
                selected_dict[new_key] = weighted_dict[key]
            else:
                selected_dict[key] = weighted_dict[key]
        
        # Format output
        formatted_output = []
        for key in selected_dict:
            item_data = selected_dict[key]
            if output_format == "simple":
                formatted_output.append(item_data['value'])
            else:  # weighted_text
                formatted_output.append(f"({item_data['value']}:{item_data['weight']})")
        
        return "\n".join(formatted_output), selected_dict

class WeightedDictConcat:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dict1": ("DICT",),
            },
            "optional": {
                "dict2": ("DICT",),
                "dict3": ("DICT",),
                "dict4": ("DICT",),
                "dict5": ("DICT",),
            }
        }
    
    RETURN_TYPES = ("DICT",)
    FUNCTION = "concat_dicts"
    CATEGORY = "llm-utils"

    def concat_dicts(self, dict1, dict2=None, dict3=None, dict4=None, dict5=None) -> tuple[Dict[str, Any]]:
        # Start with the first dictionary
        combined_items = dict1["items"].copy()
        combined_weights = dict1["weights"].copy()
        
        # Add other dictionaries if they exist
        for d in [dict2, dict3, dict4, dict5]:
            if d is not None:
                combined_items.update(d["items"])
                combined_weights.update(d["weights"])
        
        # Create the combined weighted dictionary
        weighted_dict = {
            "items": combined_items,
            "weights": combined_weights
        }

        return (weighted_dict,)
