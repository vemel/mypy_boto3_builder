"""
Jinja2-related utils.
"""

from pathlib import Path
from typing import Any

from mypy_boto3_builder.jinja_manager import JinjaManager

_jinja_manager: JinjaManager | None = None


def render_jinja2_template(template_path: Path, **kwargs: Any) -> str:
    """
    Render Jinja2 template to a string.

    Arguments:
        template_path -- Relative path to template in `TEMPLATES_PATH`
        kwargs -- Render arguments

    Returns:
        A rendered template.
    """
    global _jinja_manager
    if _jinja_manager is None:
        _jinja_manager = JinjaManager()
    template = _jinja_manager.get_template(template_path)
    return template.render(**kwargs)
