import random
from typing import Dict, Any

class WeightedDictInput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "entry_count": ("INT", {"default": 3, "min": 1, "max": 10}),
            },
            "optional": {
                **{f"key_{i+1}": ("STRING", {"default": f"key{i+1}"}) for i in range(10)},
                **{f"value_{i+1}": ("STRING", {"default": f"value{i+1}"}) for i in range(10)},
                **{f"weight_{i+1}": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 100.0}) for i in range(10)},
            }
        }
    
    RETURN_TYPES = ("DICT",)
    FUNCTION = "create_weighted_dict"
    CATEGORY = "utils"

    def create_weighted_dict(self, entry_count, **kwargs) -> tuple[Dict[str, Any]]:
        keys = []
        values = []
        weights = []
        
        # Collect the specified number of entries
        for i in range(entry_count):
            key = kwargs.get(f"key_{i+1}", f"key{i+1}")
            value = kwargs.get(f"value_{i+1}", f"value{i+1}")
            weight = kwargs.get(f"weight_{i+1}", 1.0)
            
            keys.append(key)
            values.append(value)
            weights.append(float(weight))

        # Create the weighted dictionary
        weighted_dict = {
            "items": dict(zip(keys, values)),
            "weights": dict(zip(keys, weights))
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
