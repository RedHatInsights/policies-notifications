import pytest

from .bop_service import BopSender


@pytest.mark.asyncio
async def disable_test_bop():
    bop = BopSender()
    await bop.send_email('Are you receiving', 'this lovely spam I send you?',
                         {'miburman@redhat.com', 'rhn-engineering-miburman'})
