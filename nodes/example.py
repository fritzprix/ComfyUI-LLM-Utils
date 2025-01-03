import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont

def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0) 
       
class PrintHelloWorld:     

    @classmethod
    def INPUT_TYPES(cls):
               
        return {"required": {       
                    "text": ("STRING", {"multiline": False, "default": "Hello World"}),
                    }
                }

    RETURN_TYPES = ()
    FUNCTION = "print_text"
    OUTPUT_NODE = True
    CATEGORY = "🧩 Tutorial Nodes"

    def print_text(self, text):

        print(f"Tutorial Text : {text}")
        
        return {}
        
class ConcatenateHelloWorld:     

    @classmethod
    def INPUT_TYPES(cls):
               
        return {"required": {       
                    "text1": ("STRING", {"multiline": False, "default": "Hello"}),
                    "text2": ("STRING", {"multiline": False, "default": "World"}),
                    }
                }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "concatenate_text"
    CATEGORY = "🧩 Tutorial Nodes"

    def concatenate_text(self, text1, text2):

        text_out = text1 + " " + text2
        
        return (text_out,)        
 
class HelloWorldOverlayText:

    @classmethod
    def INPUT_TYPES(cls):
               
        return {"required": {
                    "image_width": ("INT", {"default": 512, "min": 64, "max": 2048}),
                    "image_height": ("INT", {"default": 512, "min": 64, "max": 2048}),        
                    "text": ("STRING", {"multiline": True, "default": "Hello World"}),
                    "font_size": ("INT", {"default": 50, "min": 1, "max": 1024}),
                    "font_color": (["white", "black", "red", "green", "blue", "yellow"],),
                    "background_color": (["white", "black", "red", "green", "blue", "yellow"],),
                    }
                }

    RETURN_TYPES = ("IMAGE",)
    #RETURN_NAMES = ("IMAGE",)
    FUNCTION = "draw_overlay_text"
    CATEGORY = "🧩 Tutorial Nodes"

    def draw_overlay_text(self, image_width, image_height, text, 
                   font_size, font_color, background_color):
                   
        # based on https://stackoverflow.com/questions/1970807/center-middle-align-text-with-pil

        # Create a new PIL image
        new_img = Image.new("RGBA", (image_width, image_height), background_color) 
        draw = ImageDraw.Draw(new_img)

        # Define font
        font = ImageFont.truetype("arial.ttf", size=font_size) 
        
        # Get the image center
        image_center_x = image_width/2
        image_center_y = image_height/2
        
        # Draw the text, mm = text center
        draw.text((image_center_x, image_center_y), text, fill=font_color, font=font, anchor="mm")
        
        # Convert the PIL image to a torch tensor
        image_out = pil2tensor(new_img)
        
        return (image_out,)        
        
# Example usage of WeightedDictInput
input_node = WeightedDictInput()
weighted_dict = input_node.create_weighted_dict(
    entry_count=3,
    key_1="cat", value_1="meow", weight_1=2.0,
    key_2="dog", value_2="woof", weight_2=1.0,
    key_3="bird", value_3="chirp", weight_3=1.0
)

# Select from the weighted dictionary
selector = WeightedDictSelect()
for _ in range(5):
    result = selector.select_from_dict(weighted_dict[0])
    print(f"Selected: {result[0]}")        

# Example of formatting a weighted dictionary
input_node = WeightedDictInput()
weighted_dict = input_node.create_weighted_dict(
    entry_count=3,
    key_1="cat", value_1="meow", weight_1=2.0,
    key_2="dog", value_2="woof", weight_2=1.0,
    key_3="bird", value_3="chirp", weight_3=1.0
)

formatter = WeightedDict()
formatted_result = formatter.format_weighted_dict(weighted_dict[0])
print(formatted_result[0])
# Output will look like:
# cat: meow (2.0)
# dog: woof (1.0)
# bird: chirp (1.0)        

# Example of template substitution
input_node = WeightedDictInput()
weighted_dict = input_node.create_weighted_dict(
    entry_count=2,
    key_1="animal", value_1="cat", weight_1=1.0,
    key_2="sound", value_2="meow", weight_2=1.0
)

# Convert to new format
formatter = WeightedDict()
formatted_dict = formatter.reformat_dict(weighted_dict[0])

# Create prompt from template
prompt_node = WeightedDictToPrompt()
template = "A {{ animal }} that says {{ sound }}"
result = prompt_node.render_prompt(template, formatted_dict[0])
print(result[0])
# Output: "A cat that says meow"        

# Example of group selection
input_node = WeightedDictInput()
weighted_dict = input_node.create_weighted_dict(
    entry_count=4,
    key_1="cat", value_1="meow", weight_1=2.0,
    key_2="dog", value_2="woof", weight_2=1.0,
    key_3="bird", value_3="chirp", weight_3=1.0,
    key_4="cow", value_4="moo", weight_4=1.0
)

# Convert to new format
formatter = WeightedDict()
formatted_dict = formatter.reformat_dict(weighted_dict[0])

# Select group of items
group_selector = WeightedDictSelectGroup()
formatted_str, selected_dict = group_selector.select_group(
    formatted_dict[0], 
    count=2, 
    allow_duplicates=False
)

print(f"Formatted selection: {formatted_str}")
# Output example: "meow:2.0, woof:1.0"

# Use selected dict with template
prompt_node = WeightedDictToPrompt()
template = "Animals that make sounds: {{ cat }} and {{ dog }}"
result = prompt_node.render_prompt(template, selected_dict)
print(result[0])
# Output example: "Animals that make sounds: meow and woof"        