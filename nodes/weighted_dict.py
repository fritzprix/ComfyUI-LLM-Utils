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
            },
        }
    
    RETURN_TYPES = ("STRING", )
    FUNCTION = "select_from_dict"
    CATEGORY = "utils"

    def select_from_dict(self, weighted_dict: Dict[str, Any]) -> tuple[str]:
        items = weighted_dict["items"]
        weights = weighted_dict["weights"]
        
        # Get keys and their corresponding weights
        keys = list(items.keys())
        weight_values = [weights[k] for k in keys]
        
        # Select a random key based on weights
        selected_key = random.choices(keys, weights=weight_values, k=1)[0]
        selected_value = items[selected_key]
        
        return (selected_value,)

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
        
        # Replace each {{key}} with its corresponding value
        for key, data in weighted_dict.items():
            placeholder = f"{{{{ {key} }}}}"
            value = data["value"]
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
            },
        }
    
    RETURN_TYPES = ("STRING", "DICT")
    RETURN_NAMES = ("formatted_selection", "selected_dict")
    FUNCTION = "select_group"
    CATEGORY = "utils"

    def select_group(self, weighted_dict: Dict[str, Any], count: int, allow_duplicates: bool) -> tuple[str, Dict[str, Any]]:
        # Get keys and their corresponding values/weights
        keys = list(weighted_dict.keys())
        weight_values = [weighted_dict[k]["weight"] for k in keys]
        
        # Select multiple keys based on weights
        if allow_duplicates:
            selected_keys = random.choices(keys, weights=weight_values, k=count)
        else:
            # Ensure we don't request more items than available
            count = min(count, len(keys))
            selected_keys = []
            remaining_keys = keys.copy()
            remaining_weights = weight_values.copy()
            
            for _ in range(count):
                if not remaining_keys:
                    break
                # Select one key at a time
                idx = random.choices(range(len(remaining_keys)), weights=remaining_weights, k=1)[0]
                selected_keys.append(remaining_keys.pop(idx))
                remaining_weights.pop(idx)
        
        # Create formatted string output
        formatted_selections = []
        selected_dict = {}
        
        for key in selected_keys:
            value = weighted_dict[key]["value"]
            weight = weighted_dict[key]["weight"]
            formatted_selections.append(f"{value}:{weight}")
            
            # Add to selected dictionary
            selected_dict[key] = {
                "value": value,
                "weight": weight
            }
        
        formatted_output = ", ".join(formatted_selections)
        
        return (formatted_output, selected_dict)

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
