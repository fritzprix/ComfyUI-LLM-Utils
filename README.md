# ComfyUI-LLM-Utils

A collection of utility nodes for ComfyUI focused on text and LLM-related operations. Currently includes weighted dictionary nodes for dynamic text generation and manipulation.

## Features

### Weighted Dictionary Nodes

A set of nodes for working with weighted dictionaries, enabling random text selection based on weights and template-based text generation.

#### Available Nodes

##### WeightedDictInput

Creates a single weighted dictionary entry.

- Inputs:
  - key: Key for the entry
  - value: Value for the entry
  - weight: Weight for the entry (0-100)
- Output: Dictionary structure

##### WeightedDictConcat

Combines multiple weighted dictionaries into one.

- Required Input:
  - dict1: First weighted dictionary
- Optional Inputs:
  - dict2: Second weighted dictionary
  - dict3: Third weighted dictionary
  - dict4: Fourth weighted dictionary
  - dict5: Fifth weighted dictionary
- Output: Combined weighted dictionary

##### WeightedDict

Reformats the dictionary for better accessibility.

- Input: Weighted dictionary
- Output: Reformatted dictionary with value-weight pairs

##### WeightedDictSelect

Randomly selects a single value based on weights.

- Input: Weighted dictionary
- Output: Selected value

##### WeightedDictSelectGroup

Selects multiple values based on weights.

- Inputs:
  - weighted_dict: Input dictionary
  - count: Number of items to select (1-10)
  - allow_duplicates: Allow/prevent duplicate selections
- Outputs:
  - formatted_selection: "value1:weight1, value2:weight2, ..."
  - selected_dict: Dictionary of selected items

##### WeightedDictToPrompt

Generates text using templates and dictionary values.

- Inputs:
  - template: Text with placeholders (e.g., "{{ key }}")
  - weighted_dict: Values for substitution
- Output: Rendered text

## Installation

1. Clone this repository into your ComfyUI custom_nodes directory:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/your-username/ComfyUI-LLM-Utils.git
```

2. Restart ComfyUI

## Example Usage

### Basic Weighted Selection

```python
# Create individual weighted dictionary entries
input_node = WeightedDictInput()
dict1 = input_node.create_weighted_dict("cat", "meow", 2.0)[0]
dict2 = input_node.create_weighted_dict("dog", "woof", 1.0)[0]
dict3 = input_node.create_weighted_dict("bird", "chirp", 1.0)[0]

# Combine dictionaries
concat_node = WeightedDictConcat()
combined_dict = concat_node.concat_dicts(dict1, dict2, dict3)[0]

# Select based on weights
selector = WeightedDictSelect()
result = selector.select_from_dict(combined_dict)
# Possible output: "meow" (higher chance due to weight=2.0)
```

### Template-Based Text Generation

```python
# Create and combine dictionary entries
input_node = WeightedDictInput()
dict1 = input_node.create_weighted_dict("animal", "cat", 1.0)[0]
dict2 = input_node.create_weighted_dict("sound", "meow", 1.0)[0]

concat_node = WeightedDictConcat()
combined_dict = concat_node.concat_dicts(dict1, dict2)[0]

# Format the dictionary
formatter = WeightedDict()
formatted_dict = formatter.reformat_dict(combined_dict)[0]

# Generate text from template
prompt_node = WeightedDictToPrompt()
template = "A {{ animal }} that says {{ sound }}"
result = prompt_node.render_prompt(template, formatted_dict)
# Output: "A cat that says meow"
```

### Group Selection

```python
# Select multiple items
group_selector = WeightedDictSelectGroup()
formatted_str, selected_dict = group_selector.select_group(
    formatted_dict, 
    count=2, 
    allow_duplicates=False
)
# formatted_str example: "meow:2.0, woof:1.0"
```

## Testing

Run the test suite:

```bash
cd nodes
python -m unittest test_weighted_dict.py
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
