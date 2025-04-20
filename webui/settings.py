import gradio as gr
from utils.utils import *

# # Tab: Settings
# A tab to adjust the settings in configuration in config.yaml
# ## Utils
@overload
def apply_config(
    default_data: str,
    backup_dir: str,
    module_dir: str,
    module_priority: List[str]
): ...

def apply_config(default_data, backup_dir, module_dir, module_priority):
    config.default_data = default_data
    config.backup_dir = backup_dir
    config.module_dir = module_dir
    all_modules = get_modules()
    config.module_priority = module_priority
    module_ignore = [
        module for module in all_modules
        if module not in module_priority
    ]
    config.module_ignore = module_ignore
    Message("Settings saved. Restart required.")()

def reset_config():
    return (
        config.default_data,
        config.backup_dir,
        config.module_dir,
        [module for module in get_modules() if module not in config.module_ignore]
    )

def apply_color(color_preset: dict):
    config.color_preset = dict(color_preset)
    Message("Color preset saved.")()

@overload
def create() -> None: ...

def create():
    # ## UI
    with gr.Tab("Settings"):
        with gr.Row():
            with gr.Column(min_width=160):
                default_data_textbox = gr.Textbox(
                    label="Default Data Path",
                    info="Path of the YAML file to be loaded by default.",
                    interactive=True,
                    value=config.default_data
                )

                backup_dir_textbox = gr.Textbox(
                    label="Backup Directory",
                    info="Directory to save backup data.",
                    interactive=True,
                    value=config.backup_dir
                )

                module_dir_textbox = gr.Textbox(
                    label="Modules Directory",
                    info="Directory of modules.",
                    interactive=True,
                    value=config.module_dir
                )

                modules_checkboxgroup = gr.CheckboxGroup(
                    label="Modules",
                    info="Check to enable | Uncheck to disable | Re-order",
                    interactive=True,
                    choices=get_modules(),
                    value=lambda: [
                        module for module in get_modules()
                        if module not in config.module_ignore
                    ]
                )

                modules_textbox = gr.Textbox(
                    show_label=False,
                    lines=5,
                    value=lambda modules: data2yaml(modules),
                    inputs=modules_checkboxgroup
                )

                with gr.Row():
                    apply_config_button = gr.Button(
                        value="Apply",
                        variant='primary',
                        scale=21
                    )

                    reset_config_button = gr.Button(
                        value="🔄",
                        min_width=15
                    )

            with gr.Column(min_width=320, variant='panel'):
                gr.Markdown("Colors")
                color_preset = gr.State(MyDict(config.color_preset))
                @gr.render(inputs=color_preset)
                def manage_color(color_preset_value):
                    for color_name in color_preset_value:
                        with gr.Row():
                            color_textbox = gr.Textbox(
                                container=False,
                                min_width=75,
                                scale=5,
                                value=lambda: color_name
                            )

                            color_picker = gr.ColorPicker(
                                container=False,
                                min_width=240,
                                scale=16,
                                value=lambda: color_preset_value[color_name]
                            )

                            color_del_button = gr.Button(
                                value='❌',
                                min_width=15,
                                size='sm'
                            )

                            color_del_button.click(
                                lambda color_preset, color_name=color_name: color_preset.delete(color_name),
                                inputs=color_preset,
                                outputs=color_preset
                            )

                gr.Markdown("New Color")
                with gr.Row():
                    new_color_textbox = gr.Textbox(
                        container=False,
                        min_width=75,
                        scale=5,
                        interactive=True
                    )

                    new_color_picker = gr.ColorPicker(
                        container=False,
                        min_width=240,
                        scale=16,
                        interactive=True,
                        value="rgba(255, 255, 255, 1)"
                    )

                    color_add_button = gr.Button(
                        value='➕',
                        min_width=15,
                        size='sm'
                    )

                with gr.Row():
                    apply_color_button = gr.Button(
                        value="Apply",
                        variant='primary',
                        scale=21
                    )

                    reset_color_button = gr.Button(
                        value="🔄",
                        min_width=15
                    )

                # summary = gr.Textbox(
                #     label="Summary",
                #     value=lambda color_preset: data2yaml(dict(color_preset)),
                #     inputs=color_preset
                # )

        # ## Events
        apply_config_button.click(
            apply_config,
            inputs=[
                default_data_textbox,
                backup_dir_textbox,
                module_dir_textbox,
                modules_checkboxgroup
            ]
        )

        reset_config_button.click(
            reset_config,
            outputs=[
                default_data_textbox,
                backup_dir_textbox,
                module_dir_textbox,
                modules_checkboxgroup
            ]
        )

        new_color_picker.input(
            lambda color: rgba_to_name(color),
            inputs=new_color_picker,
            outputs=new_color_textbox
        )

        color_add_button.click(
            lambda color_preset, color_name, color:
            color_preset.assign({color_name: normalize_color(color)}) if color_name else color_preset,
            inputs=[color_preset, new_color_textbox, new_color_picker],
            outputs=color_preset
        )

        apply_color_button.click(
            apply_color,
            inputs=color_preset
        )

        reset_color_button.click(
            lambda: MyDict(config.color_preset),
            outputs=color_preset
        )