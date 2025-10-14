"""
Test script to verify AI categorization of brain dumps
Run this after starting the server with: ./bash_scripts/run_server
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_categorization():
    """Test that brain dumps are properly categorized"""
    print("\nTesting AI Categorization")
    print("=" * 60)

    # Test cases covering all three categories
    test_cases = [
        {
            "name": "Shopping List - Multiple Items",
            "input": "Buy groceries: milk, eggs, bread, and cheese",
            "expected_category": "shopping_list"
        },
        {
            "name": "Shopping List - Simple",
            "input": "Need milk and eggs from the store",
            "expected_category": "shopping_list"
        },
        {
            "name": "Task - With Due Date",
            "input": "Buy birthday present for Noah's party by Friday",
            "expected_category": "task"
        },
        {
            "name": "Task - Simple To-Do",
            "input": "Call the plumber about the leaky faucet",
            "expected_category": "task"
        },
        {
            "name": "Calendar Event - With Time",
            "input": "Doctor appointment on October 25th at 2:30pm",
            "expected_category": "calendar_event"
        },
        {
            "name": "Calendar Event - Soccer Practice",
            "input": "Soccer practice next Thursday at 4pm",
            "expected_category": "calendar_event"
        },
        {
            "name": "Shopping List - With Quantities",
            "input": "Get 2 gallons of milk, 1 dozen eggs, and 3 pounds of cheese",
            "expected_category": "shopping_list"
        },
        {
            "name": "Task - Reminder",
            "input": "Remember to call mom this weekend",
            "expected_category": "task"
        }
    ]

    results = {
        "passed": 0,
        "failed": 0,
        "details": []
    }

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Input: '{test_case['input']}'")
        print(f"   Expected: {test_case['expected_category']}")
        print("-" * 60)

        try:
            response = requests.post(
                f"{BASE_URL}/brain-dumps/",
                json={
                    "text": test_case["input"],
                    "user_id": 1
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                actual_category = result.get("category")

                print(f"   Actual: {actual_category}")

                # Check if categorization is correct
                if actual_category == test_case["expected_category"]:
                    print("   ✓ PASSED")
                    results["passed"] += 1

                    # Print additional details based on category
                    if actual_category == "shopping_list":
                        items = result.get("items", [])
                        print(f"   Items extracted: {len(items)}")
                        for item in items:
                            quantity = f" ({item['quantity']})" if item.get('quantity') else ""
                            print(f"     - {item['item_name']}{quantity}")
                    elif actual_category == "task":
                        print(f"   Title: {result.get('title')}")
                        if result.get('due_date'):
                            print(f"   Due Date: {result.get('due_date')}")
                    elif actual_category == "calendar_event":
                        print(f"   Title: {result.get('title')}")
                        print(f"   Date: {result.get('event_date')}")
                        if result.get('event_time'):
                            print(f"   Time: {result.get('event_time')}")

                    results["details"].append({
                        "name": test_case["name"],
                        "status": "PASSED"
                    })
                else:
                    print(f"   ✗ FAILED - Expected {test_case['expected_category']}, got {actual_category}")
                    results["failed"] += 1
                    results["details"].append({
                        "name": test_case["name"],
                        "status": "FAILED",
                        "expected": test_case["expected_category"],
                        "actual": actual_category
                    })
            else:
                print(f"   ✗ FAILED - Status code: {response.status_code}")
                print(f"   Error: {response.text}")
                results["failed"] += 1
                results["details"].append({
                    "name": test_case["name"],
                    "status": "FAILED",
                    "error": response.text
                })

        except requests.exceptions.Timeout:
            print("   ✗ FAILED - Request timed out (30s)")
            results["failed"] += 1
            results["details"].append({
                "name": test_case["name"],
                "status": "FAILED",
                "error": "Timeout"
            })
        except requests.exceptions.ConnectionError:
            print("   ✗ FAILED - Could not connect to server")
            print("   Make sure the server is running: ./bash_scripts/run_server")
            results["failed"] += 1
            break
        except Exception as e:
            print(f"   ✗ FAILED - {e}")
            results["failed"] += 1
            results["details"].append({
                "name": test_case["name"],
                "status": "FAILED",
                "error": str(e)
            })

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total = results["passed"] + results["failed"]
    print(f"Total Tests: {total}")
    print(f"Passed: {results['passed']} ({results['passed']/total*100:.1f}%)")
    print(f"Failed: {results['failed']} ({results['failed']/total*100:.1f}%)")
    print("=" * 60)

    return results


if __name__ == "__main__":
    test_categorization()
