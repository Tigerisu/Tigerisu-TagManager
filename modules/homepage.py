import gradio as gr

from utils.utils import *
from modules import add_tag, manage_color

with gr.Blocks() as home:
    # Global States
    groups = gr.State([])
    message = gr.State('')

    # # Header
    # Load .yaml file
    # ## UI
    with gr.Row():
        file_input = gr.Textbox(
            scale=2,
            value=default_yaml,
            label='Path to .yaml',
            interactive=True
        )
        with gr.Column(min_width=160):
            btn_load_yaml = gr.Button("📂 Load", variant='primary')
            btn_load_yaml.click(
                lambda file: read_yaml(file),
                inputs = file_input,
                outputs = groups
            )
            clear_groups = gr.ClearButton(
                groups,
                value="❌ Discard Data",
                size='sm',
            )

    # # Data Preview
    # Dynamically render the working data
    # ## UI
    with gr.Accordion(label="Preview"):
        with gr.Column(variant='panel'):
            current_group_name = gr.State('')
            @gr.render(inputs=[groups, current_group_name])
            def select_group(groups, cur_group_name):
                gr.Markdown("Groups")
                with gr.Row():
                    choices = OrderedSet(group['name'] for group in groups)
                    color = color_list['brown']
                    for group in groups:
                        choices.add(group['name'])
                        if group['name'] == cur_group_name:
                            color = group['color']
                    value = OrderedSet([cur_group_name])
                    group_checkboxgroup = gr.CheckboxGroup(
                        container=False,
                        scale=11,
                        interactive=True,
                        choices=choices,
                        value=list(value & choices)
                    )
                    group_checkboxgroup.input(
                        lambda group_checkboxgroup:
                        group_checkboxgroup[-1] if group_checkboxgroup else cur_group_name,
                        inputs=group_checkboxgroup,
                        outputs=current_group_name
                    )
                    show_group_color = gr.ColorPicker(
                        show_label=False,
                        value=color,
                        min_width=40,
                        visible=bool(cur_group_name)
                    )

            current_subgroup_name = gr.State('')
            @gr.render(inputs=[groups, current_group_name, current_subgroup_name])
            def select_group(groups, cur_group_name, cur_subgroup_name):
                gr.Markdown("Subgroups")
                with gr.Row():
                    choices = OrderedSet()
                    color = color_list['brown']
                    for group in groups:
                        if group['name'] == cur_group_name:
                            for subgroup in group['groups']:
                                choices.add(subgroup['name'])
                                if subgroup['name'] == cur_subgroup_name:
                                    color = subgroup['color']
                    value = OrderedSet([cur_subgroup_name])
                    subgroup_checkboxgroup = gr.CheckboxGroup(
                        container=False,
                        scale=11,
                        interactive=True,
                        choices=choices,
                        value=list(value & choices)
                        )
                    subgroup_checkboxgroup.input(
                        lambda subgroup_checkboxgroup, current_subgroup_name:
                        subgroup_checkboxgroup[-1] if subgroup_checkboxgroup else current_subgroup_name,
                        inputs=[subgroup_checkboxgroup, current_subgroup_name],
                        outputs=current_subgroup_name
                    )
                    show_subgroup_color = gr.ColorPicker(
                        show_label=False,
                        value=color,
                        min_width=40,
                        visible=bool(cur_group_name)
                    )

            @gr.render(inputs=[groups, current_group_name, current_subgroup_name])
            def show_tags(groups, cur_group_name, cur_subgroup_name):
                for group in groups:
                    if group['name'] == cur_group_name:
                        for subgroup in group['groups']:
                            if subgroup['name'] == cur_subgroup_name:
                                gr.HighlightedText(
                                    container=False,
                                    value=subgroup['tags'].items()
                                )
    # # Tabs for function
    # Currently implemented:
    # * Add Tag
    add_tag.create(groups, message)
    # * WIP: Color Management
    # manage_color.create(groups, message)
    

    # # Footage
    # Manage the yaml file
    # ## UI
    with gr.Row():
        backup_button = gr.Button("🗄️ Backup")
        save_button = gr.Button("💾 Save", variant='primary')
    message_textbox = gr.Textbox(label="Message", value=lambda message: message, inputs=message)

    # ## Event
    backup_button.click(backup_yaml, inputs=[file_input], outputs=message)
    save_button.click(write_yaml, inputs=[groups, file_input], outputs=message)