import logging

from jinja2 import Environment, PackageLoader, select_autoescape

logger = logging.getLogger(__name__)


class TemplateEngine:

    def __init__(self) -> None:
        self._env: Environment = Environment(
            loader=PackageLoader('app', 'templates'),
            autoescape=select_autoescape(['html']),
            enable_async=True
        )
        # Compile the required templates
        # self._weekly_template = self._env.get_template('custom-policies-weekly-mail.html')
        self._instant_template = self._env.get_template('custom-policies-instant-mail.html')

    async def render(self, template_type: str, params: dict):
        logger.info('Params: %s', params)
        # What sort of parameters do we need? The template to use and the event data / properties.
        rendered = await self._instant_template.render_async(params)
        return rendered
