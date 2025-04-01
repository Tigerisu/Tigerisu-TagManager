import gradio as gr
from utils.utils import *

# # Tab: Color
# Manage color preset and colors for groups and subgroups
# ## Logic
new_entry = {
    'group_color': color_list['brown'],
    'subgroup_color': color_list['brown'],
    'position': {}
}

def entry2str(entry):
    position = ''
    for group in entry['position']:
        position += f"|- {group}\n"
        for subgroup in entry['position'][group]:
            position += f"    |- {subgroup}\n"
    group_color = entry['group_color']
    subgroup_color = entry['subgroup_color']
    return f"TO\n{position}with\nNew group color: {group_color}\nNew subgroup color: {subgroup_color}"

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
    with gr.Tab("Color"):
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
                    lambda entry, group_checkboxgroup:
                    entry.update({
                        'position': {
                            group_name: entry['position'].get(group_name, []) for group_name in group_checkboxgroup
                            }
                        }) or entry,
                    inputs=[entry, group_checkboxgroup],
                    outputs=entry
                )
                clear_groups = gr.ClearButton(
                    group_checkboxgroup,
                    value="⚠️ Clear Groups",
                    size='sm'
                )
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
                apply_group = gr.Button(
                    value="Apply to Groups"
                )

            
            # @gr.render(inputs=[groups, current_group_name, entry])
            # def select_subgroup(groups, cur_group_name, entry_dict):
            #     gr.Markdown(f"Subgroups of {cur_group_name}:")
            #     choices = OrderedSet()
            #     for group in groups:
            #         if group['name'] == cur_group_name:
            #             choices.update([subgroup['name'] for subgroup in group['groups']])
            #     value = OrderedSet()
            #     if cur_group_name:
            #         value.update(entry_dict['position'].get(cur_group_name, []))
            #     subgroup_checkboxgroup = gr.CheckboxGroup(
            #         container=False,
            #         interactive=True,
            #         choices=choices,
            #         value=list(value & choices)
            #     )
            #     def subgroup_checkboxgroup_change(entry, current_group_name, subgroup_checkboxgroup):
            #         entry['position'].update({current_group_name: subgroup_checkboxgroup})
            #         if not subgroup_checkboxgroup:
            #             del entry['position'][current_group_name]
            #         return entry
            #     subgroup_checkboxgroup.change(
            #         subgroup_checkboxgroup_change,
            #         inputs=[entry, current_group_name, subgroup_checkboxgroup],
            #         outputs=entry
            #     )
            
            # @gr.render(inputs=entry)
            # def cancel_selection(entry_dict):
            #     gr.Markdown("Selected:")
            #     for group_name in entry_dict['position']:
            #         choices = OrderedSet()
            #         choices.update([subgroup_name for subgroup_name in entry_dict['position'][group_name]])
            #         selected_checkboxgroup = gr.CheckboxGroup(
            #             label=group_name,
            #             interactive=True,
            #             choices=choices,
            #             value=list(choices)
            #         )
            #         def selected_checkgroup_change(entry, selected_checkboxgroup):
            #             entry['position'].update({group_name: selected_checkboxgroup})
            #             if not selected_checkboxgroup:
            #                 del entry['position'][group_name]
            #             return entry
            #         selected_checkboxgroup.change(
            #             selected_checkgroup_change,
            #             inputs=[entry, selected_checkboxgroup],
            #             outputs=entry
            #         )
            #     clear_selection = gr.Button(
            #         value="⚠️ Clear Selection",
            #         size='sm'
            #     )
            #     clear_selection.click(
            #         lambda entry: entry.update({'position': {}}) or entry,
            #         inputs=entry,
            #         outputs=entry
            #     )

        
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
        # groups.change(
        #     update_group_checkboxgroup,
        #     inputs=[groups, entry],
        #     outputs=group_checkboxgroup
        # )

        # group_checkboxgroup.change(
        #     update_subgroup_checkboxgroup,
        #     inputs=[groups, group_checkboxgroup, entry],
        #     outputs=subgroup_checkboxgroup
        # )

        # group_color.input(
        #     update_entry,
        #     inputs=[entry, group_color, subgroup_color, subgroup_checkboxgroup],
        #     outputs=entry
        # )