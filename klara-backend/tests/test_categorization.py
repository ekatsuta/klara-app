"""
Test AI categorization of brain dumps using pytest and TestClient

Note: Brain dumps now return AI suggestions without saving to database.
To save items, use the respective save endpoints (/tasks, /shopping-items, /calendar-events).
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

    # Shopping items should return as a list of ProcessedShoppingItem (no IDs yet)
    assert isinstance(result, list)
    assert len(result) == 4

    # Verify each item has the expected structure (AI suggestions, not saved)
    for item in result:
        assert "description" in item
        # Should NOT have database fields like id, user_id, raw_input, created_at
        assert "id" not in item
        assert "user_id" not in item


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

    # Task should return as ProcessedTask (not saved to DB)
    assert isinstance(result, dict)
    assert "description" in result
    assert "due_date" in result
    assert "estimated_time_minutes" in result
    assert "should_decompose" in result
    assert "subtasks" in result
    # Should NOT have database fields
    assert "id" not in result
    assert "user_id" not in result


def test_task_simple(client, test_user):
    """Test simple task categorization (should not be decomposed)"""
    response = client.post(
        "/brain-dumps/",
        json={
            "text": "Call the plumber about the leaky faucet",
            "user_id": test_user.id,
        },
    )

    assert response.status_code == 200
    result = response.json()

    # Should return ProcessedTask
    assert isinstance(result, dict)
    assert "description" in result
    assert "estimated_time_minutes" in result
    assert "should_decompose" in result
    assert "subtasks" in result

    # Simple task should NOT be decomposed
    assert result["should_decompose"] is False
    assert len(result["subtasks"]) == 0

    # Should NOT have database fields
    assert "id" not in result
    assert "user_id" not in result


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

    # Should return ProcessedCalendarEvent (not saved to DB)
    assert isinstance(result, dict)
    assert "description" in result
    assert "event_date" in result
    assert "event_time" in result
    # Should NOT have database fields
    assert "id" not in result
    assert "user_id" not in result


def test_calendar_event_simple(client, test_user):
    """Test simple calendar event categorization"""
    response = client.post(
        "/brain-dumps/",
        json={"text": "Soccer practice next Thursday at 4pm", "user_id": test_user.id},
    )

    assert response.status_code == 200
    result = response.json()

    # Should return ProcessedCalendarEvent (not saved to DB)
    assert isinstance(result, dict)
    assert "description" in result
    assert "event_date" in result
    # Should NOT have database fields
    assert "id" not in result
    assert "user_id" not in result


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

    # Should return ProcessedTask
    assert isinstance(result, dict)
    assert "description" in result
    assert "estimated_time_minutes" in result
    assert "should_decompose" in result
    assert "subtasks" in result
    # Should NOT have database fields
    assert "id" not in result
    assert "user_id" not in result


def test_task_complex_with_decomposition(client, test_user):
    """Test complex task that should be decomposed into subtasks"""
    response = client.post(
        "/brain-dumps/",
        json={
            "text": "Plan Noah's birthday party next month",
            "user_id": test_user.id,
        },
    )

    assert response.status_code == 200
    result = response.json()

    # Should return ProcessedTask with decomposition
    assert isinstance(result, dict)
    assert "description" in result
    assert "estimated_time_minutes" in result
    assert "should_decompose" in result
    assert "reasoning" in result
    assert "subtasks" in result

    # Complex task SHOULD be decomposed
    assert result["should_decompose"] is True
    assert len(result["subtasks"]) >= 3  # Should have multiple subtasks

    # Verify subtask structure
    for subtask in result["subtasks"]:
        assert "description" in subtask
        assert "order" in subtask
        assert "estimated_time_minutes" in subtask
        # Subtask should not have database fields
        assert "id" not in subtask
        assert "parent_task_id" not in subtask

    # Should NOT have database fields
    assert "id" not in result
    assert "user_id" not in result
