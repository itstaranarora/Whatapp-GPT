"""Make some requests to OpenAI's chatbot"""

import time
import os 
import flask
import sys

from flask import g

from playwright.sync_api import sync_playwright

PROFILE_DIR = "/tmp/playwright" if '--profile' not in sys.argv else sys.argv[sys.argv.index('--profile') + 1]
PORT = 5001 if '--port' not in sys.argv else int(sys.argv[sys.argv.index('--port') + 1])
APP = flask.Flask(__name__)
PLAY = sync_playwright().start()
BROWSER = PLAY.firefox.launch_persistent_context(
    user_data_dir="/tmp/playwright",
    headless=False,
    java_script_enabled=True,
)
PAGE = BROWSER.new_page()

def get_input_box():
    """Find the input box by searching for the largest visible one."""
    textareas = PAGE.query_selector_all("textarea")
    candidate = None
    for textarea in textareas:
        if textarea.is_visible():
            if candidate is None:
                candidate = textarea
            elif textarea.bounding_box().width > candidate.bounding_box().width:
                if textarea.bounding_box().height >  candidate.bounding_box().height:
                    candidate = textarea
    return candidate

def is_logged_in():
    try:
        return get_input_box() is not None
    except AttributeError:
        return False

def send_message(message):
    # Send the message
    box = get_input_box()
    box.click()
    box.fill(message)
    box.press("Enter")
    while PAGE.query_selector(".result-streaming") is not None:
        time.sleep(0.1)

def get_last_message():
    """Get the latest message"""
    last_element = PAGE.query_selector("#chatHistory > div:last-child > [data-testid='youchat-answer'] > [data-testid='youchat-text']")
    #chatHistory &#62; :last-child [data-testid="youchat-text"]
    return last_element.inner_text()

@APP.route("/chat", methods=["GET"])
def chat():
    message = flask.request.args.get("q")
    print("Sending message: ", message)
    send_message(message)
    response = get_last_message()
    print("Response: ", response)
    return response

def start_browser():
    PAGE.goto("https://you.com/chat")
    APP.run(port=PORT, threaded=False)
    if not is_logged_in():
        print("Something went worng!")
    else:
        print("Logged in")
        
if __name__ == "__main__":
    start_browser()