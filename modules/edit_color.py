import gradio as gr
from utils.utils import *

# # Tab: Color
# Manage color preset and colors for groups and subgroups
# ## Logic
new_entry = MyDict({
    'color': config.color_list['brown'],
    'position': {}
})

@overload
def exec_entry(
    groups: dict,
    color: str,
    position_dict: dict,
    apply2groups: bool,
    apply2subgroups: bool,
    apply2subgroups_all: bool
) -> dict: ...

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
def apply2groups(
    groups: dict,
    entry: dict,
    apply2subgroups_all: bool
) -> dict: ...

def apply2groups(groups, entry, apply2subgroups_all):
    color = entry['color']
    position = entry['position']

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
    apply2groups: bool
) -> dict: ...

def apply2subgroups(groups, entry, apply2groups):
    color = entry['color']
    position = entry['position']

    if not position:
        msg = Message("Select groups.", 'warning')
        msg()
        return groups
    
    group = exec_entry(groups, color, position, apply2groups, True)
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
                            choices=list(config.color_list) + ['🎨CUSTOM'],
                            value='brown'
                        )
                        save_custom = gr.Checkbox(visible=False)
                        new_color_name = gr.Textbox(visible=False)
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

        with gr.Accordion(label="Summary", open=False):
            summary = gr.Textbox(
                container=False,
                value=data2yaml,
                inputs=entry
            )

        # ## Events
        color_dropdown.change(
            lambda entry, color_dropdown, color_picker: (
                entry.assign({'color': config.color_list.get(color_dropdown, normalize_color(color_picker))}),
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
            lambda entry, color_picker: (
                entry.assign({'color': normalize_color(color_picker)}),
                '🎨CUSTOM'
            ),
            inputs=[entry, color_picker],
            outputs=[entry, color_dropdown]
        )

        save_custom.change(
            lambda save_custom: gr.Textbox(
                label="Name",
                visible=save_custom,
            ),
            inputs=save_custom,
            outputs=new_color_name
        )

        apply_group.click(
            apply2groups,
            inputs=[groups, entry, apply2subgroups_checkbox],
            outputs=groups
        )

        apply_subgroup.click(
            apply2subgroups,
            inputs=[groups, entry, apply2groups_checkbox],
            outputs=groups
        )