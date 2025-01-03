from .nodes.weighted_dict import (
    WeightedDictInput, 
    WeightedDictSelect, 
    WeightedDict, 
    WeightedDictToPrompt,
    WeightedDictSelectGroup
)

NODE_CLASS_MAPPINGS = {
    "WeightedDictInput": WeightedDictInput,
    "WeightedDictSelect": WeightedDictSelect,
    "WeightedDict": WeightedDict,
    "WeightedDictToPrompt": WeightedDictToPrompt,
    "WeightedDictSelectGroup": WeightedDictSelectGroup
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WeightedDictInput": "Weighted Dict Input",
    "WeightedDictSelect": "Weighted Dict Select",
    "WeightedDict": "Weighted Dict",
    "WeightedDictToPrompt": "Weighted Dict To Prompt",
    "WeightedDictSelectGroup": "Weighted Dict Select Group"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
