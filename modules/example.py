import gradio as gr
from utils.utils import *

# # Tab: Name
# Description
# ## Utils
def foo():
    return

@overload
def create(groups: gr.State) -> None: ...

def create(groups):
    # ## UI
    with gr.Tab("Example"):
        text = gr.Textbox("Hello World")

    # ## Events
    text.change()