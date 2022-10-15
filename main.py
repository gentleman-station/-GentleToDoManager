#!/usr/bin/env python3

from frontend import index
from fire import Fire
import flet


def run(web: bool = False, host: str = '0.0.0.0', port: int = 55555):
    """Execute #GentleToDoManager

    Args:
        web (bool, optional): Use web version of this application while executing it. (Default: False)
    """
    if web:
        print(f"Serving a flet web app. on http://{host}:{port} (Note: Launching the URL in your default web browser.")
        flet.app(target=index, view=flet.WEB_BROWSER, host=host, port=port)
    else:
        flet.app(target=index)


if __name__ == '__main__':
    Fire(run)