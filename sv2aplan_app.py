import eel
import os, sys
from sv2aplan_tool import start

eel.init("web")


@eel.expose
def startSv2AplanTool(path: str, path_to_aplan_result: str | None = None):
    start(path, path_to_aplan_result)


@eel.expose
def onExit(*args, **kwargs):
    print("Window closed")
    sys.exit(0)


try:
    eel.start("home.html", mode="chrome", close_callback=onExit)
except Exception as e:
    print("Error with Chrome mode:", e)
    try:
        eel.start("home.html", mode="electron", close_callback=onExit)
    except Exception as e:
        print("Error with Electron mode:", e)
        try:
            eel.start("home.html", mode="edge", close_callback=onExit)
        except Exception as e:
            print("Error with Edge mode:", e)
            try:
                eel.start("home.html", mode="default", close_callback=onExit)
            except Exception as e:
                print("Error with Default mode:", e)
