import shutil
import os
import yaml
from datetime import datetime
import re
import gradio as gr

# message
class Message(str):
    def __new__(cls, content='', level='info', duration=5):
        return super().__new__(cls, content)

    def __init__(self, content='', level='info', duration=5):
        self.level = level
        self.duration = duration

    def __add__(self, other):
        return Message(super().__add__(other), self.level, self.duration)

    def __iadd__(self, other):
        return self.__add__(other)

    def __call__(self):
        match self.level:
            case 'error': gr.Error(self, self.duration)
            case 'info': gr.Info(self, self.duration)
            case 'warning': gr.Warning(self, self.duration)
            case _: raise ValueError(f"Invalid Notification Level: {self.level}")

# ordered set
class OrderedSet:
    def __init__(self, iterable=None):
        self._dict = {}  # Internal dictionary to maintain order and uniqueness
        if iterable:
            self.update(iterable)

    def add(self, item):
        """Add a single item (like set.add() or list.append())."""
        self._dict[item] = None  # Using dict keys to ensure uniqueness

    def update(self, iterable):
        """Add multiple items (like list.extend() or set.update())."""
        for item in iterable:
            self._dict[item] = None

    def __and__(self, other):
        """Perform intersection with another OrderedSet."""
        if not isinstance(other, OrderedSet):
            return NotImplemented
        return OrderedSet(k for k in self._dict if k in other._dict)

    def __iter__(self):
        """Iterate over elements in order."""
        return iter(self._dict.keys())

    def __contains__(self, item):
        """Check if an item exists in the OrderedSet."""
        return item in self._dict

    def __len__(self):
        """Get the number of elements in the OrderedSet."""
        return len(self._dict)

    def __repr__(self):
        """String representation of the OrderedSet."""
        return f"OrderedSet({list(self._dict.keys())})"

# init vaiables
with open("config.yaml", 'r', encoding='utf-8') as config_file:
    config = yaml.safe_load(config_file)
default_yaml = config['default_yaml']
backup_dir = config['backup_dir']
color_list = config['color_list']

# file I/O
def read_yaml(filepath=default_yaml):
    if not os.path.exists(filepath): return []
    with open(filepath, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    return data

def write_yaml(data, filepath=default_yaml):
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True, sort_keys=False)
    Message(f"Successfully saved to: {filepath}")()

def backup_yaml(filepath=default_yaml, backup_dir=backup_dir):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    filename = os.path.basename(filepath)
    file_name, file_ext = os.path.splitext(filename)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    backup_filename = f"{file_name}_{timestamp}{file_ext}"

    backup_path = os.path.join(backup_dir, backup_filename)

    shutil.copy(filepath, backup_path)

    Message(f"Successfully backed up to: {backup_path}")()

# take in a list or dict
# return in yaml style string
def data2yaml(entry):
    return yaml.dump(entry, default_flow_style=False, allow_unicode=True, sort_keys=False)

# take in a string of color in hex or rgba format
# return the color a rgba format with each channel rounded to int and A set to 1
def normalize_color(color: str) -> str:
    if color.startswith("#"):
        color = color.lstrip("#")
        if len(color) == 6:
            r, g, b = int(color[:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        else:
            raise ValueError("Invalid hex color format")
    elif color.startswith("rgba"):
        match = re.match(r"rgba\(([\d.]+),\s*([\d.]+),\s*([\d.]+),\s*[\d.]+\)", color)
        if not match:
            raise ValueError("Invalid rgba color format")
        r, g, b = map(float, match.groups())
    else:
        raise ValueError("Unsupported color format")

    return f"rgba({round(r)}, {round(g)}, {round(b)}, 1)"