from .tools import create_identity_header, create_broken_identity_header


def test_subscriptions(client):
    headers = {'x-rh-identity': create_identity_header('000001', 'test_account').decode()}

    response = client.put("/endpoints/email/subscription/policies-daily-mail", headers=headers)
    assert response.status_code == 204

    # Redoing should cause no errors
    response = client.put("/endpoints/email/subscription/policies-daily-mail", headers=headers)
    assert response.status_code == 204

    # Check the subscription status
    response = client.get("/endpoints/email/subscription/policies-daily-mail", headers=headers)
    assert response.status_code == 200
    json_payload = response.json()
    assert json_payload is not None
    assert json_payload['status'] == 'Subscribed'

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


def test_webhooks(client):
    headers = {'x-rh-identity': create_identity_header('000001', 'test_user').decode()}

    # print('Header: {}'.format(headers))

    payload = {
        'name': 'Test endpoint',
        'description': 'Just a test',
        'enabled': 'true',
        'properties': {
            'url': 'https://webhook.site/bca343cf-c11c-4125-b065-22e1411a73e0',
            'method': 'POST',
            'disable_ssl_verification': 'false',
            'secret_token': 'superSecretToken'
        }
    }

    response = client.post("/endpoints", headers=headers, json=payload)
    # TODO Test that 400 (422) is correctly used if there's a validation error in the data
    # print(response.json())
    # TODO Fix to 200 and check the returned data
    assert response.status_code == 204

    response = client.get("/endpoints", headers=headers)
    assert response.status_code == 200

    json_payload = response.json()
    assert json_payload is not None
    assert len(json_payload) == 1
    id = json_payload[0]['id']
    assert id is not None

    response = client.get("/endpoints/{}".format(id), headers=headers)
    json_payload = response.json()
    assert json_payload is not None
    assert json_payload['id'] == id

    response = client.get("/endpoints/{}/history".format(id), headers=headers)
    assert response.status_code == 200

    json_payload = response.json()
    assert len(json_payload) == 0
