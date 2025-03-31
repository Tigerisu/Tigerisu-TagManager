import gradio as gr
from utils.utils import *

# # Tab: Name
# Description
# ## Logic
def foo():
    return

def create(groups, message):
    # ## UI
    with gr.Tab("Color"):
        text = gr.Textbox("Hello World")

    # ## Events
    text.change()