import gradio as gr
from utils.utils import *

# # Tab: Color
# Manage color preset and colors for groups and subgroups
# ## Logic
new_entry = MyDict({
    'color': "rgba(255, 255, 255, 1)",
    'position': {}
})

@overload
def exec_entry(
    groups: dict,
    color: str,
    position_dict: dict,
    apply2groups: bool,
    apply2subgroups: bool,
    apply2subgroups_all: bool,
) -> list: ...

def exec_entry(groups, color, position_dict, apply2groups, apply2subgroups, apply2subgroups_all):
    msg = Message(duration=5)
    for group in groups:
        if group['name'] in position_dict:
            # found a selected group
            # set color if apply color to groups
            if apply2groups:
                group['color'] = color
                msg += f"Apply color to {group['name']}.\n"
            if apply2subgroups_all:
                # apply to all subgroups
                # set color
                for subgroup in group['groups']:
                    subgroup['color'] = color
                msg += f"Apply color to all subgroups of {group['name']}.\n"
            elif apply2subgroups:
                # apply to selected subgroups
                subgroups_selected = position_dict[group['name']]
                for subgroup in group['groups']:
                    if subgroup['name'] in subgroups_selected:
                        # found a selected subgroup
                        # set color
                        subgroup['color'] = color
                        msg += f"Apply color to {group['name']} -> {subgroup['name']}.\n"
    msg()
    return groups

@overload
def save_custom_color(
    color_name: str,
    color: str
): ...

def save_custom_color(color_name, color):
    config.color_preset[color_name] = color
    config.save_config()
    Message("Color saved.")()

@overload
def apply2groups(
    groups: dict,
    entry: dict,
    apply2subgroups_all: bool,
    color_name: str,
    save_custom: bool
) -> list: ...

def apply2groups(groups, entry, apply2subgroups_all, color_name, save_custom):
    color = entry['color']
    position = entry['position']

    if save_custom:
        save_custom_color(color_name, color)

    if not position:
        msg = Message("Select groups.", 'warning')
        msg()
        return groups
    
    groups = exec_entry(groups, color, position, True, False, apply2subgroups_all)
    return groups

@overload
def apply2subgroups(
    groups: dict,
    entry: dict,
    apply2groups: bool,
    color_name: str,
    save_custom: bool
) -> list: ...

def apply2subgroups(groups, entry, apply2groups, color_name, save_custom):
    color = entry['color']
    position = entry['position']

    if save_custom:
        save_custom_color(color_name, color)

    if not position:
        msg = Message("Select groups.", 'warning')
        msg()
        return groups
    
    groups = exec_entry(groups, color, position, apply2groups, True, False)
    return groups

@overload
def create(groups: gr.State) -> None: ...

def create(groups):
    # ## UI
    with gr.Tab("Edit Color"):
        entry = gr.State(new_entry)
        with gr.Column(variant='panel'):
            @overload
            def select_group(
                groups: dict,
                entry_value: dict
            ) -> None: ...

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
                
                group_checkboxgroup.change(
                    lambda group_checkboxgroup:
                    entry_value.assign({
                        'position': {
                            group_name: entry_value['position'].get(group_name, []) for group_name in group_checkboxgroup
                            }
                        }),
                    inputs=group_checkboxgroup,
                    outputs=entry
                )

            @overload
            def select_subgroup(
                groups: dict,
                entry_value: dict
            ) -> None: ...

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
                            entry_value['position'].assign({group['name']: subgroup_checkboxgroup}) and entry_value,
                            inputs=subgroup_checkboxgroup,
                            outputs=entry
                        )
            clear_selection = gr.Button(
                value="⚠️ Clear Selection",
                size='sm'
            )
            clear_selection.click(
                lambda entry: entry.assign({'position': {}}),
                inputs=entry,
                outputs=entry
            )

        with gr.Row():
            with gr.Column(variant='panel'):
                gr.Markdown("Color")
                with gr.Row():
                    with gr.Column(min_width=100, scale=2):
                        color_dropdown = gr.Dropdown(
                            container=False,
                            interactive=True,
                            allow_custom_value=True,
                            choices=list(config.color_preset),
                            value=None
                        )

                        save_custom = gr.Checkbox(
                            label="Save Custom Color",
                            interactive=True,
                            value=lambda color_dropdown: not color_dropdown in config.color_preset,
                            inputs=color_dropdown
                        )
                    
                    color_picker = gr.ColorPicker(
                        container=False,
                        min_width=240,
                        scale=3,
                        interactive=True,
                        value=lambda entry: entry['color'],
                        inputs=entry
                    )
            with gr.Column(min_width=240):
                with gr.Row():
                    apply_group = gr.Button(
                        value="Apply to Groups",
                        variant='primary'
                    )
                    apply2subgroups_checkbox = gr.Checkbox(
                        label="Apply to all subgroups of selected groups."
                    )
                with gr.Row():
                    apply_subgroup = gr.Button(
                        value="Apply to Subgroups",
                        variant='primary'
                    )
                    apply2groups_checkbox = gr.Checkbox(
                        label="Apply to all groups of selected subgroups."
                    )

        # with gr.Accordion(label="Summary", open=False):
        #     summary = gr.Textbox(
        #         container=False,
        #         value=data2yaml,
        #         inputs=entry
        #     )

        gr.Markdown("<center>‼️ Remember to save your file. ‼️</center>")

        # ## Events
        color_dropdown.input(
            lambda entry, color_dropdown: (
                entry.assign({'color': config.color_preset[color_dropdown]})
                if color_dropdown in config.color_preset else entry
            ),
            inputs=[entry, color_dropdown],
            outputs=entry
        )

        color_picker.input(
            lambda entry, color_picker: (
                entry.assign({'color': normalize_color(color_picker)}),
                rgba_to_name(color_picker)
            ),
            inputs=[entry, color_picker],
            outputs=[entry, color_dropdown]
        )

        apply_group.click(
            apply2groups,
            inputs=[groups, entry, apply2subgroups_checkbox, color_dropdown, save_custom],
            outputs=groups
        )

        apply_subgroup.click(
            apply2subgroups,
            inputs=[groups, entry, apply2groups_checkbox, color_dropdown, save_custom],
            outputs=groups
        )