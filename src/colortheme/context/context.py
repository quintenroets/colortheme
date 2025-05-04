from package_utils.context import Context

from .options import Options

context = Context[Options, None, None](Options, None, None)
