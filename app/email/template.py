import logging
from datetime import datetime

from jinja2 import Environment, PackageLoader, select_autoescape, TemplateNotFound, StrictUndefined

from ..core.errors import NoTemplateFoundException

logger = logging.getLogger(__name__)


def dateformat(value, format='%d %b %Y'):
    return value.strftime(format)


def datetimeformat(value, format='%d %b %H:%M UTC'):
    return value.strftime(format)


class TemplateEngine:
    def __init__(self) -> None:
        self._env: Environment = Environment(
            loader=PackageLoader('app', 'templates'),
            autoescape=select_autoescape(['html']), undefined=StrictUndefined,
            enable_async=True
        )
        self._env.filters['dateformat'] = dateformat
        self._env.filters['datetimeformat'] = datetimeformat

    async def render(self, template_type: str, params: dict):
        params['now'] = datetime.now()
        try:
            template = self._env.get_template(template_type + '.html')
        except TemplateNotFound as e:
            raise NoTemplateFoundException(e)

        rendered = await template.render_async(params)
        return rendered
