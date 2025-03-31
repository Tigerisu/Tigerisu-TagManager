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

def exec_entry(groups, text, desc, position_dict, new_group_color, new_subgroup_color, message):
    if not position_dict:
        message = "Select groups and subgroups."
        return groups, message

    for group in groups:
        if group['name'] in position_dict:
            # group exists
            message += f"Group \"{group['name']}\" exists.\n"
            subgroups_selected = position_dict[group['name']]
            for subgroup in group['groups']:
                if subgroup['name'] in subgroups_selected:
                    # subgroup exists
                    message += f"Subgroup \"{subgroup['name']}\" exists.\n"
                    # create/update tag
                    if text:
                        subgroup['tags'][text] = desc
                        message += f"Successfully added tag \"{text} ({desc})\".\n"
                    subgroups_selected.remove(subgroup['name'])
            if subgroups_selected:
                # new subgroup
                subgroup_name = subgroups_selected[0]
                message += f"Subgroup \"{subgroup_name}\" does not exist.\n"
                # create subgroup
                group['groups'].append({
                    'name': subgroup_name,
                    'color': new_subgroup_color,
                    'tags': {text: desc} if text else {}
                })
                message += f"Successfully  added subgroup \"{subgroup_name}\".\n"
                if text:
                    message += f"Successfully added tag \"{text} ({desc})\".\n"
            del position_dict[group['name']]
    if position_dict:
        # new group
        group_name = next(iter(position_dict))
        subgroup_name = position_dict[group_name][0]
        message += f"Group {group_name} does not exist.\n"
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
        message += f"Successfully  added group \"{group_name}\".\n"
        message += f"Successfully  added subgroup \"{subgroup_name}\".\n"
        if text:
            message += f"Successfully added tag \"{text} ({desc})\".\n"
    return groups, message

def add_tag(groups, entry):
    message = "ADD TAG\n"
    text = entry['text']
    desc = entry['desc']
    position = entry['position']
    new_group_color = entry['new_group_color']
    new_subgroup_color = entry['new_subgroup_color']

    if not text:
        message = "Text is empty."
        return groups, text, desc, message
    
    groups, message = exec_entry(groups, text, desc, position, new_group_color, new_subgroup_color, message)

    text = ''
    desc = ''
    return groups, text, desc, message

def add_group(groups, entry):
    message = "ADD GROUP\n"
    position = entry['position']
    new_group_color = entry['new_group_color']
    new_subgroup_color = entry['new_subgroup_color']
    
    groups, message = exec_entry(groups, None, None, position, new_group_color, new_subgroup_color, message)

    return groups, message


def create(groups, message):
    # ## UI
    with gr.Tab("ADD"):
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
            current_group_name = gr.State('')
            @gr.render(inputs=[groups, new_group_name, current_group_name])
            def select_group(groups, new_group_name, cur):
                gr.Markdown("Groups")
                choices = OrderedSet(group['name'] for group in groups)
                if new_group_name:
                    choices.add(new_group_name)
                value = OrderedSet([cur])
                group_checkboxgroup = gr.CheckboxGroup(
                    container=False,
                    interactive=True,
                    choices=choices,
                    value=list(value & choices)
                )
                group_checkboxgroup.input(
                    lambda group_checkboxgroup, current_group_name:
                    group_checkboxgroup[-1] if group_checkboxgroup else current_group_name,
                    inputs=[group_checkboxgroup, current_group_name],
                    outputs=current_group_name
                )

            @gr.render(inputs=[groups, new_subgroup_name, current_group_name, entry])
            def select_subgroup(groups, new_subgroup_name, cur_group_name, entry_dict):
                gr.Markdown(f"Subgroups of {cur_group_name}:")
                choices = OrderedSet()
                for group in groups:
                    if group['name'] == cur_group_name:
                        choices.update([subgroup['name'] for subgroup in group['groups']])
                if cur_group_name and new_subgroup_name:
                    choices.add(new_subgroup_name)
                value = OrderedSet()
                if cur_group_name:
                    value.update(entry_dict['position'].get(cur_group_name, []))
                subgroup_checkboxgroup = gr.CheckboxGroup(
                    container=False,
                    interactive=True,
                    choices=choices,
                    value=list(value & choices)
                )
                def subgroup_checkboxgroup_change(entry, current_group_name, subgroup_checkboxgroup):
                    entry['position'].update({current_group_name: subgroup_checkboxgroup})
                    if not subgroup_checkboxgroup:
                        del entry['position'][current_group_name]
                    return entry
                subgroup_checkboxgroup.change(
                    subgroup_checkboxgroup_change,
                    inputs=[entry, current_group_name, subgroup_checkboxgroup],
                    outputs=entry
                )
            
            @gr.render(inputs=entry)
            def cancel_selection(entry_dict):
                gr.Markdown("Selected:")
                for group_name in entry_dict['position']:
                    choices = OrderedSet()
                    choices.update([subgroup_name for subgroup_name in entry_dict['position'][group_name]])
                    selected_checkboxgroup = gr.CheckboxGroup(
                        label=group_name,
                        interactive=True,
                        choices=choices,
                        value=list(choices)
                    )
                    def selected_checkgroup_change(entry, selected_checkboxgroup):
                        entry['position'].update({group_name: selected_checkboxgroup})
                        if not selected_checkboxgroup:
                            del entry['position'][group_name]
                        return entry
                    selected_checkboxgroup.change(
                        selected_checkgroup_change,
                        inputs=[entry, selected_checkboxgroup],
                        outputs=entry
                    )
                clear_selection = gr.Button(
                    value="⚠️ Clear Selection",
                    size='sm'
                )
                clear_selection.click(
                    lambda entry: entry.update({'position': {}}) or entry,
                    inputs=entry,
                    outputs=entry
                )

        # summary = gr.Textbox(
        #     label="Summary",
        #     value=lambda x: entry2str(x),
        #     inputs=entry
        # )
        
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
            outputs=[groups, message]
        )

        add_tag_button.click(
            add_tag,
            inputs=[groups, entry],
            outputs=[groups, text, desc, message]
        )