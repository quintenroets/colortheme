from __future__ import annotations

from plib import Path as BasePath


class Path(BasePath):
    root = BasePath(__file__).parent
    assets = root / "assets"
    script_templates = assets / "kde_script_templates"
