"""Happy-path tests for FastAPI application endpoints."""

import pytest


class TestRootEndpoint:
    """Tests for GET / root endpoint."""

    def test_redirect_root_to_static(self, client):
        """Verify root endpoint redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all(self, client):
        """Verify /activities returns all available activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        
        # Verify we have all 9 expected activities
        expected_activities = {
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Soccer Club", "Art Club",
            "Drama Club", "Debate Club", "Science Club"
        }
        assert set(activities.keys()) == expected_activities

    def test_activities_contain_expected_fields(self, client):
        """Verify each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        # Check that each activity has the required fields
        required_fields = {"description", "schedule", "max_participants", "participants"}
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict), f"{activity_name} is not a dict"
            assert required_fields.issubset(activity_data.keys()), \
                f"{activity_name} missing fields: {required_fields - set(activity_data.keys())}"
            
            # Verify field types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_activity_success(self, client):
        """Verify student successfully signs up for an activity."""
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]

    def test_signup_adds_participant_to_list(self, client):
        """Verify student appears in activity's participants list after signup."""
        email = "newstudent@mergington.edu"
        activity_name = "Programming Class"
        
        # Get initial participants count
        response = client.get("/activities")
        initial_participants = response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)
        
        # Sign up new student
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Verify student was added
        response = client.get("/activities")
        updated_participants = response.json()[activity_name]["participants"]
        assert len(updated_participants) == initial_count + 1
        assert email in updated_participants


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client):
        """Verify student successfully unregisters from an activity."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # This student is pre-registered
        
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]

    def test_unregister_removes_participant_from_list(self, client):
        """Verify student is removed from activity's participants list after unregister."""
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # This student is pre-registered
        
        # Get initial participants count
        response = client.get("/activities")
        initial_participants = response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)
        assert email in initial_participants
        
        # Unregister student
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Verify student was removed
        response = client.get("/activities")
        updated_participants = response.json()[activity_name]["participants"]
        assert len(updated_participants) == initial_count - 1
        assert email not in updated_participants


class TestStaticFileServing:
    """Tests for static file serving."""

    def test_serve_index_html(self, client):
        """Verify /static/index.html is served successfully."""
        response = client.get("/static/index.html")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        # Verify it contains expected HTML content
        assert "<title>Mergington High School Activities</title>" in response.text

    def test_serve_app_js(self, client):
        """Verify /static/app.js is served successfully."""
        response = client.get("/static/app.js")
        assert response.status_code == 200
        assert "javascript" in response.headers.get("content-type", "")
        # Verify it contains expected JavaScript
        assert "DOMContentLoaded" in response.text
