from dataclasses import dataclass
from typing import Annotated

import typer

from .action import Action


@dataclass
class Options:
    action: Annotated[Action, typer.Argument(help="The action to do")] = Action.check
