import pytest




@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post(
        "/auth/register",
        json={"username": "valera", "password": "test1234"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "valera"
    assert "id" in data
    assert "hashed_password" not in data



@pytest.mark.asyncio
async def test_register_duplicate(client):
    await client.post("/auth/register", json={"username": "valera", "password": "test1234"})
    response = await client.post(
        "/auth/register",
        json={"username": "valera", "password": "test1234"},
    )
    assert response.status_code == 400



@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/auth/register", json={"username": "valera", "password": "test1234"})
    data = await client.post("/auth/token", data={"username": "valera", "password": "test1234"})
    assert data.status_code == 200
    data_json = data.json()
    assert "access_token" in data_json



@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/auth/register", json={"username": "valera", "password": "test1234"})
    data = await client.post("/auth/token", data={"username": "valera", "password": "test123"})
    assert data.status_code == 401