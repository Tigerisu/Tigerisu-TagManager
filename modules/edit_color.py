import gradio as gr
from utils.utils import *

# # Tab: Color
# Manage color preset and colors for groups and subgroups
# ## Logic
new_entry = {
    'color': color_list['brown'],
    'position': {}
}

# def submit_entry(groups, entry):
#     message = ""
#     group_color = entry['group_color']
#     subgroup_color = entry['subgroup_color']
#     position = entry['position']

#     if not position:
#         message = "Select groups and subgroups for tag."
#         return groups, message
    
#     position_dict = group_subgroup_names_to_dict(position)

#     for group in groups:
#         if group['name'] in position_dict:
#             # group exists
#             group['color'] = group_color
#             message += f"Set group \"{group['name']}\" to color {group_color}.\n"
#             subgroups_selected = position_dict[group['name']]
#             for subgroup in group['groups']:
#                 if subgroup['name'] in subgroups_selected:
#                     # subgroup exists
#                     subgroup['color'] = subgroup_color
#                     message += f"Set subgroup \"{subgroup['name']}\" to color {subgroup_color}.\n"
#     return groups, message

def create(groups):
    # ## UI
    with gr.Tab("Edit Color"):
        entry = gr.State(new_entry)
        with gr.Column(variant='panel'):
            @gr.render(inputs=[groups, entry])
            def select_group(groups, entry_value):
                gr.Markdown("Groups")
                choices = OrderedSet(group['name'] for group in groups)
                value = OrderedSet(entry_value['position'])
                group_checkboxgroup = gr.CheckboxGroup(
                    container=False,
                    interactive=True,
                    choices=choices,
                    value=list(value & choices)
                )
                def update_entry_groups(entry, group_checkboxgroup):
                    for group_name in group_checkboxgroup:
                        entry['position'].setdefault(group_name, [])
                    return entry
                group_checkboxgroup.change(
                    lambda group_checkboxgroup:
                    entry_value.update({
                        'position': {
                            group_name: entry_value['position'].get(group_name, []) for group_name in group_checkboxgroup
                            }
                        }) or entry_value,
                    inputs=group_checkboxgroup,
                    outputs=entry
                )
            @gr.render(inputs=[groups, entry])
            def select_subgroup(groups, entry_value):
                for group in groups:
                    if group['name'] in entry_value['position']:
                        gr.Markdown(f"Subgroups of {group['name']}")
                        choices = OrderedSet([subgroup['name'] for subgroup in group['groups']])
                        value = OrderedSet(entry_value['position'].get(group['name'], []))
                        subgroup_checkboxgroup = gr.CheckboxGroup(
                            container=False,
                            interactive=True,
                            choices=choices,
                            value=list(value & choices)
                        )
                        subgroup_checkboxgroup.change(
                            lambda subgroup_checkboxgroup, group=group:
                            entry_value['position'].update({group['name']: subgroup_checkboxgroup})
                            or entry_value,
                            inputs=subgroup_checkboxgroup,
                            outputs=entry
                        )

        with gr.Row():
            with gr.Column():
                color_dropdown = gr.Dropdown(
                    label='Color',
                    interactive=True,
                    choices=list(color_list) + ['🎨CUSTOM'],
                    value='brown',
                    min_width=80,
                )
                save_custom = gr.Checkbox(
                    label="Save custom color",
                    interactive=True,
                    visible=False
                )
            color_picker = gr.ColorPicker(
                label="Group Color",
                interactive=True,
                value=lambda entry: entry['color'],
                inputs=entry,
            )
            with gr.Column():
                apply2subgroups = gr.Checkbox(
                    label="Apply to all subgroups of selected groups."
                )
                apply_group = gr.Button(
                    value="Apply to Groups"
                )

        summary = gr.Textbox(
            label="Summary",
            value=data2yaml,
            inputs=entry
        )

        # ## Events
        color_dropdown.change(
            lambda entry, color_dropdown, color_picker: (
                entry.update({'color': color_list.get(color_dropdown, normalize_color(color_picker))}) or entry,
                gr.Checkbox(
                    label="Save custom color",
                    interactive=True,
                    visible=(color_dropdown == '🎨CUSTOM'),
                    value=True
                )
            ),
            inputs=[entry, color_dropdown, color_picker],
            outputs=[entry, save_custom]
        )

        color_picker.input(
            lambda entry, color_picker: 
            (entry.update({'color': normalize_color(color_picker)}) or entry, '🎨CUSTOM'),
            inputs=[entry, color_picker],
            outputs=[entry, color_dropdown]
        )