import logging

from jinja2 import Environment, PackageLoader, select_autoescape

from ..core.errors import NoTemplateFoundException

logger = logging.getLogger(__name__)


class TemplateEngine:

    def __init__(self) -> None:
        self._env: Environment = Environment(
            loader=PackageLoader('app', 'templates'),
            autoescape=select_autoescape(['html']),
            enable_async=True
        )

    async def render(self, template_type: str, params: dict):
        logger.info('Params: %s', params)
        # What sort of parameters do we need? The template to use and the event data / properties.
        template = self._env.get_template(template_type + '.html')
        if template is None:
            raise NoTemplateFoundException('No template found for type %s', template_type)
        rendered = await template.render_async(params)
        return rendered
