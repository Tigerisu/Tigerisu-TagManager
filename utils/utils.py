import shutil
import os
import yaml
from datetime import datetime

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

# general purpose functions
def read_yaml(filepath=default_yaml):
    if not os.path.exists(filepath): return []
    with open(filepath, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    return data

def write_yaml(data, filepath=default_yaml):
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return f"Successfully saved to: {filepath}"

def backup_yaml(filepath=default_yaml, backup_dir=backup_dir):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    filename = os.path.basename(filepath)
    file_name, file_ext = os.path.splitext(filename)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    backup_filename = f"{file_name}_{timestamp}{file_ext}"

    backup_path = os.path.join(backup_dir, backup_filename)

    shutil.copy(filepath, backup_path)

    return f"Successfully backed up to: {backup_path}"

# turn yaml file storing tags into a string
def yaml2str(groups):
    output = ""
    for group in groups:
        group_name = group['name']
        group_color = group['color']
        output += f"{group_name} | {group_color}\n"
        subgroups = group['groups']
        for subgroup in subgroups:
            subgroup_name = subgroup['name']
            subgroup_color = subgroup['color']
            output += f'  |-- {subgroup_name} | {subgroup_color}\n'
            tags = subgroup['tags']
            for tag in tags:
                output += f'    |-- {tag}: {tags[tag]}\n'
    return output

# # input: ["group_name1 | subgroup_name2", "group_name1 | subgroup_name2"]
# # output: {"group_name1": ["subgroup_name1", "subgroup_name2"]}
# def group_subgroup_names_to_dict(group_subgroup_names):
#     position_dict = {}
#     for group_subgroup_name in group_subgroup_names:
#         group_name, subgroup_name = group_subgroup_name.split(' | ')
#         position_dict.setdefault(group_name, []).append(subgroup_name)
#     return position_dict