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
    CATEGORY = "utils"

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
        return {
            "required": {
                "weighted_dict": ("DICT",),
                "key": ("STRING", {"default": ""}),
                "output_format": (["simple", "weighted_text"], {"default": "simple"}),
            },
        }
    
    RETURN_TYPES = ("STRING", )
    FUNCTION = "select_from_dict"
    CATEGORY = "utils"

    def _format_value(self, key, item_data, format_type):
        """Helper method to format a single value based on format type."""
        if format_type == "simple":
            return item_data['value']
        elif format_type == "weighted_text":
            return f"({item_data['value']}:{item_data['weight']})"
        return item_data['value']  # fallback to simple

    def select_from_dict(self, weighted_dict: Dict[str, Any], key: str, output_format: str = "simple") -> tuple[str]:
        items = weighted_dict["items"]
        
        # Get value for the specified key
        if key not in items:
            raise ValueError(f"Key '{key}' not found in weighted dictionary")
            
        selected_item = items[key]
        formatted_value = self._format_value(key, selected_item, output_format)
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
    CATEGORY = "utils"

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
    CATEGORY = "utils"

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
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "weighted_dict": ("DICT",),
                "count": ("INT", {"default": 3, "min": 1, "max": 10}),
                "allow_duplicates": ("BOOLEAN", {"default": False}),
                "output_format": (["simple", "weighted_text"], {"default": "simple"}),
            },
            "optional": {
                "selected_keys": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "key1,key2,key3"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "DICT")
    RETURN_NAMES = ("formatted_selection", "selected_dict")
    FUNCTION = "select_group"
    CATEGORY = "utils"

    def _parse_key_string(self, key_string: str) -> list[str]:
        """Parse a string of keys into a list, handling various formats."""
        if not key_string or key_string is None:
            return []
            
        # First split by comma or semicolon
        parts = []
        current = []
        in_quotes = False
        
        for char in key_string:
            if char == '"' or char == "'":
                in_quotes = not in_quotes
            elif char in [',', ';'] and not in_quotes:
                parts.append(''.join(current))
                current = []
            else:
                current.append(char)
                
        # Add the last part
        if current:
            parts.append(''.join(current))
            
        # Clean up each part
        cleaned_keys = []
        for part in parts:
            # Remove quotes, whitespace, and skip empty strings
            key = part.strip(' \'"')
            if key:  # Only add non-empty keys
                cleaned_keys.append(key)
                
        return cleaned_keys

    def _format_value(self, key, item_data, format_type):
        """Helper method to format a single value based on format type."""
        if format_type == "simple":
            return item_data['value']
        elif format_type == "weighted_text":
            return f"({item_data['value']}:{item_data['weight']})"
        return item_data['value']  # fallback to simple

    def select_group(self, weighted_dict, count, allow_duplicates=False, output_format="simple", key_string=None):
        if not key_string or key_string.strip() == "" or all(c in ",; " for c in key_string):
            # Fall back to random selection when key_string is empty or contains only separators
            keys = list(weighted_dict.keys())
            if not allow_duplicates:
                count = min(count, len(keys))
            selected_keys = random.sample(keys, count) if not allow_duplicates else [random.choice(keys) for _ in range(count)]
        else:
            # Handle specific key selection
            selected_keys = self._parse_key_string(key_string)
            
            # Validate all keys exist before processing
            invalid_keys = [k for k in selected_keys if k not in weighted_dict]
            if invalid_keys:
                raise ValueError(f"Invalid key(s) found in selection: {', '.join(invalid_keys)}")
            
            if not allow_duplicates:
                selected_keys = list(dict.fromkeys(selected_keys))
            selected_keys = selected_keys[:count]

        selected_dict = {k: weighted_dict[k] for k in selected_keys}
        
        # Format output
        formatted_output = ""
        for key in selected_dict:
            formatted_value = self._format_value(key, selected_dict[key], output_format)
            formatted_output += f"{formatted_value}\n"
        
        return formatted_output.strip(), selected_dict

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
    CATEGORY = "utils"

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
