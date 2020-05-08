from .tools import create_identity_header, create_broken_identity_header


def test_subscriptions(client):
    headers = {'x-rh-identity': create_identity_header('test_account', '000001').decode()}

    response = client.put("/endpoints/email/subscription/policies-daily-mail", headers=headers)
    assert response.status_code == 204

    # Redoing should cause no errors
    response = client.put("/endpoints/email/subscription/policies-daily-mail", headers=headers)
    assert response.status_code == 204

    # Check the subscription status
    response = client.get("/endpoints/email/subscription/policies-daily-mail", headers=headers)
    assert response.status_code == 200
    json = response.json()
    assert json is not None
    assert json['status'] == 'Subscribed'

    # Delete
    response = client.delete("/endpoints/email/subscription/policies-daily-mail", headers=headers)
    assert response.status_code == 204

    # No error should happen if we unsubscribe multiple times
    response = client.delete("/endpoints/email/subscription/policies-daily-mail", headers=headers)
    assert response.status_code == 204

    # Subscription should no longer exists
    response = client.get("/endpoints/email/subscription/policies-daily-mail", headers=headers)
    assert response.status_code == 404


def test_subscriptions_auth(client):
    # Without x-rh-identity header
    response = client.put("/endpoints/email/subscription/policies-daily-mail")
    assert response.status_code == 403

    # With incorrect structure of x-rh-identity
    broken_headers = {'x-rh-identity': create_broken_identity_header().decode()}
    response = client.put("/endpoints/email/subscription/policies-daily-mail", headers=broken_headers)
    assert response.status_code == 401
