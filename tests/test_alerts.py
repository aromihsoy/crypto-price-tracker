import pytest




@pytest.mark.asyncio
async def test_create_alert_requires_auth(client):
    response = await client.post("/alerts", json={"symbol": "BYTC", "condition": "gt", "threshold": 500})
    assert response.status_code == 401



@pytest.mark.asyncio
async def test_alert_privacy(client, make_user):
    user1 = await make_user("valera", "test1234")
    user2 = await make_user("valeron", "test1234")
    alert1 = await client.post("/alerts", json={"symbol": "USDT", "condition": "lt", "threshold": 1000}, headers=user1)
    alert1 = alert1.json()
    alert_id = alert1["id"]

    query = await client.get(f"/alerts/{alert_id}", headers=user2)
    assert query.status_code == 404