import gradio as gr
from utils.utils import *

# # Tab: Name
# Description
# ## Logic
def foo():
    return

def create(groups):
    # ## UI
    with gr.Tab("Example"):
        text = gr.Textbox("Hello World")

    # ## Events
    text.change()