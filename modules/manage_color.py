import gradio as gr
from utils.utils import *

# # Tab: Color
# Manage color preset and colors for groups and subgroups
# ## Logic
new_entry = {
    'group_color': color_list['brown'],
    'subgroup_color': color_list['brown'],
    'position': []
}

def submit_entry(groups, entry):
    message = ""
    group_color = entry['group_color']
    subgroup_color = entry['subgroup_color']
    position = entry['position']

    if not position:
        message = "Select groups and subgroups for tag."
        return groups, message
    
    position_dict = group_subgroup_names_to_dict(position)

    for group in groups:
        if group['name'] in position_dict:
            # group exists
            group['color'] = group_color
            message += f"Set group \"{group['name']}\" to color {group_color}.\n"
            subgroups_selected = position_dict[group['name']]
            for subgroup in group['groups']:
                if subgroup['name'] in subgroups_selected:
                    # subgroup exists
                    subgroup['color'] = subgroup_color
                    message += f"Set subgroup \"{subgroup['name']}\" to color {subgroup_color}.\n"
    return groups, message

def create(groups, message):
    # ## UI
    with gr.Tab("Color"):
        entry = gr.State(new_entry)

        group_checkboxgroup = gr.CheckboxGroup(label="Groups")
        subgroup_checkboxgroup = gr.CheckboxGroup(label="Subgroups")
        with gr.Row():
            group_color = gr.Dropdown(
                label='Group Color',
                interactive=True,
                choices=list(color_list) + ['🎨CUSTOM'],
                value='brown',
                min_width=80,
            )
            group_colorpicker = gr.ColorPicker(
                label="Group Color",
                interactive=True,
                value=lambda entry: entry['group_color'],
                inputs=entry,
                scale=2
            )
        with gr.Row():
            subgroup_color = gr.Dropdown(
                label='Subgroup Color',
                interactive=True,
                choices=list(color_list) + ['🎨CUSTOM'],
                value='brown',
                min_width=80,
            )
            subgroup_colorpicker = gr.ColorPicker(
                label="Subgroup Color",
                interactive=True,
                value=lambda entry: entry['subgroup_color'],
                inputs=entry,
                scale=2
            )

        summary = gr.Textbox(label="Summary", value=entry2str, inputs=entry)

        # ## Events
        groups.change(
            update_group_checkboxgroup,
            inputs=[groups, entry],
            outputs=group_checkboxgroup
        )

        group_checkboxgroup.change(
            update_subgroup_checkboxgroup,
            inputs=[groups, group_checkboxgroup, entry],
            outputs=subgroup_checkboxgroup
        )

        group_color.input(
            update_entry,
            inputs=[entry, group_color, subgroup_color, subgroup_checkboxgroup],
            outputs=entry
        )