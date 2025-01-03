# ComfyUI-LLM-Utils

A collection of utility nodes for ComfyUI focused on text and LLM-related operations. Currently includes weighted dictionary nodes for dynamic text generation and manipulation.

## Examples

![alt text](<Screenshot from 2025-01-04 07-01-47.png>)

## Features

### Weighted Dictionary Nodes

A set of nodes for working with weighted dictionaries, enabling text selection and template-based text generation.

#### Available Nodes

##### WeightedDictInput

Creates a single weighted dictionary entry.

**Input**

- `key` (STRING): Key for the entry
- `value` (STRING): Value for the entry
- `weight` (FLOAT): Weight for the entry (default: 1.0)

**Output**

- `dictionary` (DICT): Dictionary structure containing the entry

##### WeightedDictConcat

Combines multiple weighted dictionaries into one.

**Input**

- `dict1` (DICT): First weighted dictionary (required)
- `dict2` (DICT): Second weighted dictionary (optional)
- `dict3` (DICT): Third weighted dictionary (optional)
- `dict4` (DICT): Fourth weighted dictionary (optional)
- `dict5` (DICT): Fifth weighted dictionary (optional)

**Output**

- `dictionary` (DICT): Combined weighted dictionary

##### WeightedDictSelect

Selects a specific value from the dictionary.

**Input**

- `weighted_dict` (DICT): Input dictionary
- `key` (STRING): Key to select
- `output_format` (COMBO): ["simple", "weighted_text"]
  - simple: returns just the value
  - weighted_text: returns "(value:weight)" format

**Output**

- `text` (STRING): Selected value in specified format

##### WeightedDictSelectGroup

Selects multiple values based on specified keys.

**Input**

- `weighted_dict` (DICT): Input dictionary
- `allow_duplicates` (BOOLEAN): Allow duplicate selections (default: False)
- `output_format` (COMBO): ["simple", "weighted_text"]
  - simple: returns just the values
  - weighted_text: returns "(value:weight)" format
- `selected_keys` (STRING): Comma-separated list of keys to select (e.g., "key1,key2,key3")

**Output**

- `formatted_output` (STRING): Selected values in specified format (one per line)
- `selected_dict` (DICT): Dictionary containing selected items

##### WeightedDictToPrompt

Generates text using templates and dictionary values.

**Input**

- `template` (STRING): Text with placeholders (e.g., "{{ key }}")
- `weighted_dict` (DICT): Dictionary containing values for substitution

**Output**

- `text` (STRING): Rendered text with substituted values

## Installation

1. Clone this repository into your ComfyUI custom_nodes directory:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/your-username/ComfyUI-LLM-Utils.git
```

2. Restart ComfyUI

## ComfyUI Workflow Examples

### Basic Text Selection

1. Create a WeightedDictInput node
   - Set key: "greeting"
   - Set value: "hello"
   - Set weight: 1.0

2. Create another WeightedDictInput node
   - Set key: "name"
   - Set value: "world"
   - Set weight: 1.0

3. Connect both to a WeightedDictConcat node

4. Connect to WeightedDictSelectGroup
   - Set selected_keys: "greeting,name"
   - Set output_format: "simple"

Result will be:

```
hello
world
```

### Template Text Generation

1. Create dictionary entries as above

2. Connect combined dictionary to WeightedDictToPrompt
   - Set template: "{{ greeting }} {{ name }}!"

Result will be:

```
hello world!
```

## Testing

Run the test suite from the project root:

```bash
python -m unittest discover tests
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
