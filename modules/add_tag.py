import gradio as gr
from utils.utils import *

# # Tab: Add Tag
# Add new tag to the selected group and subgroup
# ## Utils
new_entry = {
    'text': '',
    'desc': '',
    'position': {},
    'new_group_color': color_list['brown'],
    'new_subgroup_color': color_list['brown']
}

def exec_entry(groups, text, desc, position_dict, new_group_color, new_subgroup_color):
    msg = Message(duration=10)
    for group in groups:
        if group['name'] in position_dict:
            # group exists
            subgroups_selected = position_dict[group['name']]
            for subgroup in group['groups']:
                if subgroup['name'] in subgroups_selected:
                    # subgroup exists
                    # create/update tag
                    if text:
                        subgroup['tags'][text] = desc
                        msg += f"Successfully added tag \"{text} ({desc})\".\n"
                    subgroups_selected.remove(subgroup['name'])
            if subgroups_selected:
                # new subgroup
                subgroup_name = subgroups_selected[0]
                # create subgroup
                group['groups'].append({
                    'name': subgroup_name,
                    'color': new_subgroup_color,
                    'tags': {text: desc} if text else {}
                })
                msg += f"Successfully  added subgroup \"{subgroup_name}\".\n"
                if text:
                    msg += f"Successfully added tag \"{text} ({desc})\".\n"
            del position_dict[group['name']]
    if position_dict:
        # new group
        group_name = next(iter(position_dict))
        subgroup_name = position_dict[group_name][0]
        # create group
        groups.append({
            'name': group_name,
            'color': new_group_color,
            'groups': [{
                'name': subgroup_name,
                'color': new_subgroup_color,
                'tags': {text: desc} if text else {}
            }]
        })
        msg += f"Successfully  added group \"{group_name}\".\n"
        msg += f"Successfully  added subgroup \"{subgroup_name}\".\n"
        if text:
            msg += f"Successfully added tag \"{text} ({desc})\".\n"
        msg()
    return groups

def add_tag(groups, entry):
    text = entry['text']
    desc = entry['desc']
    position = entry['position']
    new_group_color = entry['new_group_color']
    new_subgroup_color = entry['new_subgroup_color']

    if not text:
        msg = Message("Text is empty.", 'warning')
        msg()
        return groups, text, desc
    
    if not position:
        msg = Message("Select groups and subgroups.", 'warning')
        msg()
        return groups, text, desc
    
    groups = exec_entry(groups, text, desc, position, new_group_color, new_subgroup_color)

    text = ''
    desc = ''
    return groups, text, desc

def add_group(groups, entry):
    position = entry['position']
    new_group_color = entry['new_group_color']
    new_subgroup_color = entry['new_subgroup_color']

    if not position:
        msg = Message("Select groups and subgroups.", 'warning')
        msg()
        return groups
    
    groups = exec_entry(groups, None, None, position, new_group_color, new_subgroup_color)

    return groups


def create(groups):
    # ## UI
    with gr.Tab("Add Tag"):
        entry = gr.State(new_entry)
        with gr.Row():
            with gr.Column(min_width=160):
                text = gr.Textbox(
                    label='Text',
                    placeholder='1girl',
                    show_copy_button=True
                )
                desc = gr.Textbox(
                    label='Description',
                    placeholder='一个女孩',
                    show_copy_button=True
                )
            with gr.Column(variant='panel',min_width=160):
                gr.Markdown("New Group Name")
                new_group_name = gr.Textbox(
                    container=False,
                    interactive=True
                )
                gr.Markdown("New Group Color")
                with gr.Row():
                    new_group_color = gr.Dropdown(
                        container=False,
                        interactive=True,
                        choices=color_list,
                        value='brown',
                        min_width=80,
                        scale=2
                    )
                    show_group_color = gr.ColorPicker(
                        show_label=False,
                        value=lambda entry: entry['new_group_color'],
                        inputs=entry,
                        min_width=40
                    )
                gr.Markdown("New Subgroup Name")
                new_subgroup_name = gr.Textbox(
                    container=False,
                    interactive=True
                )
                gr.Markdown("New Subgroup Color")
                with gr.Row():
                    new_subgroup_color = gr.Dropdown(
                        container=False,
                        interactive=True,
                        choices=color_list,
                        value='brown',
                        min_width=80,
                        scale=2
                    )
                    show_subgroup_color = gr.ColorPicker(
                        show_label=False,
                        value=lambda entry: entry['new_subgroup_color'],
                        inputs=entry,
                        min_width=40
                    )

        with gr.Column(variant='panel'):
            group_selected_names = gr.State([])
            @gr.render(inputs=[groups, new_group_name, group_selected_names])
            def select_group(groups, new_group_name, group_selected_names_value):
                gr.Markdown("Groups")
                choices = OrderedSet(group['name'] for group in groups)
                if new_group_name:
                    choices.add(new_group_name)
                value = OrderedSet(group_selected_names_value)
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
                    lambda group_checkboxgroup: group_checkboxgroup,
                    inputs=group_checkboxgroup,
                    outputs=group_selected_names
                )

            @gr.render(inputs=[groups, group_selected_names, new_group_name, new_subgroup_name, entry])
            def select_subgroup(groups, group_selected_names, new_group_name, new_subgroup_name, entry_value):
                def create_subgroup_checkboxgroup(group_name, subgroups):
                    gr.Markdown(f"Subgroups of {group_name}")
                    choices = OrderedSet([subgroup['name'] for subgroup in subgroups])
                    if new_subgroup_name:
                        choices.add(new_subgroup_name)
                    value = OrderedSet(entry_value['position'].get(group_name, []))
                    subgroup_checkboxgroup = gr.CheckboxGroup(
                        container=False,
                        interactive=True,
                        choices=choices,
                        value=list(value & choices)
                    )
                    subgroup_checkboxgroup.change(
                        lambda subgroup_checkboxgroup, group_name=group_name: (
                            entry_value['position'].update({group_name: subgroup_checkboxgroup})
                            if subgroup_checkboxgroup
                            else (entry_value['position'].pop(group_name, None) and None)
                        ) or entry_value,
                        inputs=subgroup_checkboxgroup,
                        outputs=entry
                    )
                for group in groups:
                    if group['name'] in group_selected_names:
                        create_subgroup_checkboxgroup(group['name'], group['groups'])
                if new_group_name in group_selected_names:
                    create_subgroup_checkboxgroup(new_group_name, [])

            clear_selection = gr.Button(
                value="⚠️ Clear Selection",
                size='sm'
            )
            clear_selection.click(
                lambda entry: (
                    entry.update({'position': {}}) or entry,
                    []
                ),
                inputs=entry,
                outputs=[entry, group_selected_names]
            )

        with gr.Accordion(label="Summary", open=False):
            summary = gr.Textbox(
                label="Summary",
                value=data2yaml,
                inputs=entry
            )
        
        with gr.Row():
            add_group_button = gr.Button("🗂️ Add Group")
            add_tag_button = gr.Button("➕ Add Tag", variant='primary')

        # ## Events
        text.input(
            lambda entry, text: entry.update({'text': text}) or entry,
            inputs=[entry, text],
            outputs=entry
        )

        desc.input(
            lambda entry, desc: entry.update({'desc': desc}) or entry,
            inputs=[entry, desc],
            outputs=entry
        )

        new_group_color.input(
            lambda entry, color: (
                entry.update({'new_group_color': color}) or entry,
                color
            ),
            inputs=[entry, new_group_color],
            outputs=[entry, new_subgroup_color]
        )

        new_subgroup_color.change(
            lambda entry, color: entry.update({'new_subgroup_color': color}) or entry,
            inputs=[entry, new_subgroup_color],
            outputs=entry
        )

        add_group_button.click(
            add_group,
            inputs=[groups, entry],
            outputs=groups
        )

        add_tag_button.click(
            add_tag,
            inputs=[groups, entry],
            outputs=[groups, text, desc]
        )