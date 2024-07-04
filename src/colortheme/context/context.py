from package_utils.context import Context

from colortheme.models import Config, Options, Secrets

context = Context(Options, Config, Secrets)
