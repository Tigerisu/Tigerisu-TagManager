import shutil
import os
import re
import importlib.util
from pathlib import Path
from datetime import datetime
import webcolors
from typing import overload, Tuple, List
import yaml
import gradio as gr

# init vaiables from config
class Config():
    def __init__(self):
        with open("config.yaml", 'r', encoding='utf-8') as config_file:
            self.config = yaml.safe_load(config_file)
        self.default_data = self.config['default_data']
        self.backup_dir = self.config['backup_dir']
        self.module_dir = self.config['module_dir']
        self.module_priority = self.config['module_priority']
        self.module_ignore = self.config['module_ignore']
        self.color_preset = self.config['color_preset']

    def save_config(self):
        with open("config.yaml", 'w', encoding='utf-8') as file:
            yaml.dump(self.config, file, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def set_default_data(self, default_data):
        self.config['default_data'] = default_data
        self.default_data = self.config['default_data']
        self.save_config()

    def set_backup_dir(self, backup_dir):
        self.config['backup_dir'] = backup_dir
        self.backup_dir = self.config['backup_dir']
        self.save_config()

    def set_module_dir(self, module_dir):
        self.config['module_dir'] = module_dir
        self.module_dir = self.config['module_dir']
        self.save_config()

    def set_module_priority(self, module_priority):
        self.config['module_priority'] = module_priority
        self.module_priority = self.config['module_priority']
        self.save_config()

    def set_module_ignore(self, module_ignore):
        self.config['module_ignore'] = module_ignore
        self.module_ignore = self.config['module_ignore']
        self.save_config()

    def set_color_preset(self, color_preset):
        self.config['color_preset'] = dict(color_preset)
        self.color_preset = self.config['color_preset']
        self.save_config()

config = Config()

# Message
# essentially a str which can be initialized with a level and duration
# can be modified with + and += like a string
# create a gradio pop-up message when called
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

# Ordered set
# Acts like a set without duplicate item
# but does not mess up with item order
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

# Entry
# A dict with an extra function 'assign'
# which performs like dict.update() updating only one entry
# using direct assignment for better efficiency
# and returns the dict
# Handy for lambda functions
# Recursive: keeps all dict in MyDict a MyDict
class MyDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert nested dicts into MyDict
        for key, value in self.items():
            if isinstance(value, dict) and not isinstance(value, MyDict):
                self[key] = MyDict(value)

    def __setitem__(self, key, value):
        # Convert value into MyDict if it's a dict
        if isinstance(value, dict) and not isinstance(value, MyDict):
            value = MyDict(value)
        super().__setitem__(key, value)

    def assign(self, item: dict):
        key, value = next(iter(item.items()))
        self[key] = value
        return self
    
    def delete(self, key):
        del self[key]
        return self

# file I/O
def read_yaml(filepath: str=config.default_data):
    if not os.path.exists(filepath): return []
    with open(filepath, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    return data

def write_yaml(data: dict, filepath: str=config.default_data):
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True, sort_keys=False)
    Message(f"Successfully saved to: {filepath}")()

def backup_yaml(filepath: str=config.default_data, backup_dir: str=config.backup_dir):
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
def data2yaml(data: dict):
    return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)

# Color
# given a color in rgba string, get its name
def rgba_to_name(rgba_str: str):
    parts = normalize_color(rgba_str).strip("rgba() ").split(",")
    r, g, b = map(lambda x: int(float(x)), parts[:3])
    try:
        return webcolors.rgb_to_name((r, g, b))
    except ValueError:
        return closest_color_name((r, g, b))

def closest_color_name(rgb_tuple: Tuple[str]):
    min_distance = float('inf')
    closest_name = None
    for name in webcolors.names():
        hex_code = webcolors.name_to_hex(name)
        cr, cg, cb = webcolors.hex_to_rgb(hex_code)
        distance = (rgb_tuple[0] - cr) ** 2 + (rgb_tuple[1] - cg) ** 2 + (rgb_tuple[2] - cb) ** 2
        if distance < min_distance:
            min_distance = distance
            closest_name = name
    return closest_name

# given a color name, get its rgba string
def name_to_rgba(name: str):
    try:
        rgb = webcolors.name_to_rgb(name if name else 'white')
        return f"rgba({rgb.red}, {rgb.green}, {rgb.blue}, 1)"
    except ValueError:
        return f"rgba(0, 0, 0, 1)"

# get a list of color names with length ascending
def list_color_names():
    return sorted(webcolors.names(), key=len)

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

def get_modules():
    module_dir = Path(config.module_dir)
    all_paths = list(module_dir.glob("*.py"))

    return [path.name for path in all_paths]

def create_modules(data: gr.State):
    module_dir = Path(config.module_dir)
    all_paths = list(module_dir.glob("*.py"))

    priority_paths = [module_dir / file for file in config.module_priority]
    remaining_paths = [
        path for path in all_paths
        if path.name not in config.module_priority
        and path.name not in config.module_ignore
    ]

    module_paths = priority_paths + remaining_paths
    for path in module_paths:
        try:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "create"):
                print(f"Calling {module}.create()")
                module.create(data)
            else:
                print(f"{module} has no callable create()")
        except Exception as e:
            print(f"Failed to import {module}: {e}")