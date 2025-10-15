"""
Test AI categorization of brain dumps using pytest and TestClient
"""


def test_shopping_items_multiple(client, test_user):
    """Test categorization of multiple shopping items"""
    response = client.post(
        "/brain-dumps/",
        json={
            "text": "Buy groceries: milk, eggs, bread, and cheese",
            "user_id": test_user.id,
        },
    )

    assert response.status_code == 200
    result = response.json()

    # Shopping items should return as a list
    assert isinstance(result, list)
    assert len(result) == 4

    # Verify each item has the expected structure
    for item in result:
        assert "id" in item
        assert "user_id" in item
        assert "description" in item
        assert "raw_input" in item
        assert item["user_id"] == test_user.id


def test_shopping_items_simple(client, test_user):
    """Test simple shopping items"""
    response = client.post(
        "/brain-dumps/",
        json={"text": "Need milk and eggs from the store", "user_id": test_user.id},
    )

    assert response.status_code == 200
    result = response.json()

    assert isinstance(result, list)
    assert len(result) == 2


def test_task_with_due_date(client, test_user):
    """Test task categorization with due date"""
    response = client.post(
        "/brain-dumps/",
        json={
            "text": "Buy birthday present for Noah's party by Friday",
            "user_id": test_user.id,
        },
    )

    assert response.status_code == 200
    result = response.json()

    # Task should return as a single object (not a list)
    assert isinstance(result, dict)
    assert "due_date" in result
    assert "description" in result
    assert result["user_id"] == test_user.id


def test_task_simple(client, test_user):
    """Test simple task categorization"""
    response = client.post(
        "/brain-dumps/",
        json={
            "text": "Call the plumber about the leaky faucet",
            "user_id": test_user.id,
        },
    )

    assert response.status_code == 200
    result = response.json()

    assert isinstance(result, dict)
    assert "description" in result
    assert result["user_id"] == test_user.id


def test_calendar_event_with_time(client, test_user):
    """Test calendar event categorization with time"""
    response = client.post(
        "/brain-dumps/",
        json={
            "text": "Doctor appointment on October 25th at 2:30pm",
            "user_id": test_user.id,
        },
    )

    assert response.status_code == 200
    result = response.json()

    assert isinstance(result, dict)
    assert "event_date" in result
    assert "event_time" in result
    assert "description" in result
    assert result["user_id"] == test_user.id


def test_calendar_event_simple(client, test_user):
    """Test simple calendar event categorization"""
    response = client.post(
        "/brain-dumps/",
        json={"text": "Soccer practice next Thursday at 4pm", "user_id": test_user.id},
    )

    assert response.status_code == 200
    result = response.json()

    assert isinstance(result, dict)
    assert "event_date" in result
    assert "description" in result
    assert result["user_id"] == test_user.id


def test_shopping_items_with_quantities(client, test_user):
    """Test shopping items with quantities"""
    response = client.post(
        "/brain-dumps/",
        json={
            "text": "Get 2 gallons of milk, 1 dozen eggs, and 3 pounds of cheese",
            "user_id": test_user.id,
        },
    )

    assert response.status_code == 200
    result = response.json()

    assert isinstance(result, list)
    assert len(result) == 3


def test_task_reminder(client, test_user):
    """Test task reminder categorization"""
    response = client.post(
        "/brain-dumps/",
        json={"text": "Remember to call mom this weekend", "user_id": test_user.id},
    )

    assert response.status_code == 200
    result = response.json()

    assert isinstance(result, dict)
    assert "description" in result
    assert result["user_id"] == test_user.id
