from ..events.models import Notification
from .template import TemplateEngine
from .bop_service import BopSender


class EmailProcessor:
    render_template = 'instant_mail'

    def __init__(self) -> None:
        self.rendering = TemplateEngine()
        self.sender = BopSender()

    async def process(self, notification: Notification):
        account_id: str = notification.tenantId

        email = await self.rendering.render(self.render_template, notification.dict())

        # receivers = await fetch_receivers(account_id)
        await self.sender.send_email(email, 'time@after.time')
