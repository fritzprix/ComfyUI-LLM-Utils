# ComfyUI-LLM-Utils

A collection of utility nodes for ComfyUI focused on text and LLM-related operations. Currently includes weighted dictionary nodes for dynamic text generation and manipulation.

## Features

### Weighted Dictionary Nodes

A set of nodes for working with weighted dictionaries, enabling random text selection based on weights and template-based text generation.

#### Available Nodes

##### WeightedDictInput

Creates a weighted dictionary with customizable entries.

- Inputs:
  - entry_count: Number of entries (1-10)
  - key_N: Key for entry N
  - value_N: Value for entry N
  - weight_N: Weight for entry N (0-100)
- Output: Dictionary structure

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
# Create a weighted dictionary
input_node = WeightedDictInput()
weighted_dict = input_node.create_weighted_dict(
    entry_count=3,
    key_1="cat", value_1="meow", weight_1=2.0,
    key_2="dog", value_2="woof", weight_2=1.0,
    key_3="bird", value_3="chirp", weight_3=1.0
)

# Select based on weights
selector = WeightedDictSelect()
result = selector.select_from_dict(weighted_dict[0])
# Possible output: "meow" (higher chance due to weight=2.0)
```

### Template-Based Text Generation

```python
# Create and format dictionary
input_node = WeightedDictInput()
weighted_dict = input_node.create_weighted_dict(
    entry_count=2,
    key_1="animal", value_1="cat", weight_1=1.0,
    key_2="sound", value_2="meow", weight_2=1.0
)
formatter = WeightedDict()
formatted_dict = formatter.reformat_dict(weighted_dict[0])

# Generate text from template
prompt_node = WeightedDictToPrompt()
template = "A {{ animal }} that says {{ sound }}"
result = prompt_node.render_prompt(template, formatted_dict[0])
# Output: "A cat that says meow"
```

### Group Selection

```python
# Select multiple items
group_selector = WeightedDictSelectGroup()
formatted_str, selected_dict = group_selector.select_group(
    formatted_dict[0], 
    count=2, 
    allow_duplicates=False
)
# formatted_str example: "meow:2.0, woof:1.0"
```

## Testing

Run the test suite:

```bash
python -m unittest tests/test_weighted_dict.py
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
