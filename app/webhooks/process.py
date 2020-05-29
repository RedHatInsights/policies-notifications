import logging

import aiohttp

from ..events.models import Action
from ..db import endpoints
from ..models.endpoints import Endpoint, WebhookAttributes, NotificationHistory

logger = logging.getLogger(__name__)

"""
    TODO: Retry in case of temporary errors
    TOOD: Disable the endpoint if the error can't be retried - user must manually fix the issue
    TODO: Concurrency? Here or consume?
"""


def request_tracer(results_collector):
    async def on_request_start(session, context, params):
        context.on_request_start = session.loop.time()
        context.is_redirect = False

    async def on_request_end(session, context, params):
        total = session.loop.time() - context.on_request_start
        context.on_request_end = total

        results_collector['total'] = round(total * 1000, 2)

    async def on_request_exception(session, context, params):
        total = session.loop.time() - context.on_request_start
        context.on_request_end = total
        results_collector['total'] = round(total * 1000, 2)
        results_collector['details'] = {
            'method': params.method,
            'url': str(params.url),
            'error': type(params.exception).__name__
        }
        # exception=ClientConnectorError(ConnectionKey(host='webhssssssook.site', port=443, is_ssl=True, ssl=None,
        # proxy=None, proxy_auth=None, proxy_headers_hash=-1738310210140354566),
        # gaierror(-2, 'Name or service not known')))
        # Might have strerror

    trace_config = aiohttp.TraceConfig()

    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_end.append(on_request_end)
    trace_config.on_request_exception.append(on_request_exception)

    return trace_config


class WebhookProcessor:
    timeout = aiohttp.ClientTimeout(total=3)

    async def _call_webhook(self, properties: WebhookAttributes, payload: dict) -> dict:
        if properties.disable_ssl_verification:
            ssl_verification = False
        else:
            # Default SSL verification method
            ssl_verification = None

        headers = {}

        if properties.secret_token is not None:
            headers['X-Insights-Token'] = properties.secret_token

        details = {}

        success = False
        disable = False
        retry = False

        try:
            async with aiohttp.ClientSession(headers=headers, connector=aiohttp.TCPConnector(ssl=ssl_verification),
                                             timeout=self.timeout, trace_configs=[request_tracer(details)]) as session:
                async with session.request(properties.method, properties.url, json=payload) as resp:
                    if resp.status == 200:
                        success = True
                    elif 400 <= resp.status < 500:
                        # Can't recover from this error
                        disable = True
                    else:
                        retry = True  # Maybe a temporary error - do we want to retry?

                    if not success:
                        details['details'] = {
                            'url': properties.url,
                            'method': properties.method,
                            'code': resp.status,
                            'response_body': await resp.text()
                        }

        except Exception:
            # Handled in the on_exception .. we don't to pass this forward
            pass

        details['success'] = success
        details['disable'] = disable
        details['retry'] = retry

        return details

    async def process(self, action: Action):
        account_id: str = action.tenantId
        endpoint_id: str = action.properties['endpoint_id']
        endpoint: Endpoint = await endpoints.get_endpoint(account_id, endpoint_id)

        # payload = transform(endpoint.properties.payload_transformer, action)
        payload = action.__dict__

        if endpoint.enabled:
            details: dict = await self._call_webhook(endpoint.properties, payload)
            notif_history: NotificationHistory = NotificationHistory(account_id=account_id, endpoint_id=endpoint_id,
                                                                     invocation_time=details['total'],
                                                                     invocation_result=details['success'])
            if 'details' in details:
                notif_history.details = details['details']
            await endpoints.create_history_event(notif_history)
            # TODO What about other error codes - should transformers handle them? Such as Slack's failure codes.
            # TODO And transient failures? Connection time outs etc..
        else:
            return
