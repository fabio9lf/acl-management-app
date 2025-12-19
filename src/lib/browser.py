import webbrowser
import os

def is_wsl():
    return "microsoft" in os.uname().release.lower()

def add_browser():
    webbrowser.register('windows-default', None, webbrowser.BackgroundBrowser("/mnt/c/Windows/explorer.exe"))

def open_browser():
    if is_wsl():
        add_browser()
        webbrowser.get('windows-default').open("http://localhost:5000")
    else:
        webbrowser.open("http://localhost:5000")