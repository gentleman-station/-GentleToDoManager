#!/usr/bin/env python3

from frontend import index
from fire import Fire
import flet


def run(execute: bool = True, web: bool = False):
    """Execute #GentleToDoManager

    Args:
        execute (bool, optional): Weather to execute this application. (Default: True)
        web (bool, optional): Use web version of this application while executing it. (Default: False)
    """
    if execute:
        if web:
            flet.app(target=index, view=flet.WEB_BROWSER)
        else:
            flet.app(target=index)


if __name__ == '__main__':
    Fire(run)