from tests.tools import create_identity_header


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

    # Test correct create
    response = client.post("/endpoints", headers=headers, json=payload)
    assert response.status_code == 201
    json_payload = response.json()
    assert json_payload is not None
    assert json_payload['id'] is not None
    assert json_payload['properties'] is not None

    # Test a missing field
    payload.pop('name')
    response = client.post("/endpoints", headers=headers, json=payload)
    assert response.status_code == 422  # 422 is when model can't be accepted (validation error etc)

    # Get endpoints
    response = client.get("/endpoints", headers=headers)
    assert response.status_code == 200

    json_payload = response.json()
    assert json_payload is not None
    assert len(json_payload) == 1
    id = json_payload[0]['id']
    assert id is not None

    # Get a single endpoint
    response = client.get("/endpoints/{}".format(id), headers=headers)
    json_payload = response.json()
    assert json_payload is not None
    assert json_payload['id'] == id

    # Get non-UUID endpoint
    response = client.get("/endpoints/{}".format('not_here'), headers=headers)
    assert response.status_code == 400

    # Try to get non-existant endpoint
    response = client.get("/endpoints/{}".format('c79a9247-6253-48f8-b09f-b166309d0415'), headers=headers)
    assert response.status_code == 404

    # Get endpoint's empty history
    response = client.get("/endpoints/{}/history".format(id), headers=headers)
    assert response.status_code == 200

    json_payload = response.json()
    assert len(json_payload) == 0

    # Delete endpoint
    response = client.delete("/endpoints/{}".format(id), headers=headers)
    assert response.status_code == 204

    # Assert that it really was deleted
    response = client.get("/endpoints/{}".format(id), headers=headers)
    assert response.status_code == 404

    # Verify that second delete doesn't break anything
    response = client.delete("/endpoints/{}".format(id), headers=headers)
    assert response.status_code == 204   # Or should we have 404 here?

    # Another test.. verify that history etc are also deleted
    response = client.get("/endpoints/{}/history".format(id), headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 0
