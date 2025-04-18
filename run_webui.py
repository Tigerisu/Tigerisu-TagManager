import argparse
from webui import homepage

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Gradio APP for tag management.")
    parser.add_argument('--in-browser', action='store_true', default=False, help="Automatically open the webui in browser.")
    args = parser.parse_args()
    homepage.home.launch(inbrowser=args.in_browser)