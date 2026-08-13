"""Mock tools — fully implemented, pre-built for you.

These 4 functions simulate external services (weather API, CI system, docs, ticketing).
They return hardcoded data so you don't need any API keys.
"""


def get_weather(city: str) -> dict:
    """Return mock weather data for a city.

    Args:
        city: City name (case-insensitive); known: Mumbai, Pune, Bangalore.

    Returns:
        On success: {"success": True, "data": {"city": str, "temp_c": int,
                     "condition": str, "humidity": int}}
        On miss:    {"success": False, "error": str}
    """
    mock_data = {
        "mumbai": {"city": "Mumbai", "temp_c": 32, "condition": "Humid", "humidity": 85},
        "pune": {"city": "Pune", "temp_c": 28, "condition": "Partly Cloudy", "humidity": 65},
        "bangalore": {"city": "Bangalore", "temp_c": 24, "condition": "Rainy", "humidity": 78},
    }
    key = city.lower().strip()
    if key in mock_data:
        return {"success": True, "data": mock_data[key]}
    return {"success": False, "error": f"No weather data available for '{city}'"}


def get_build_status(repo: str, branch: str) -> dict:
    """Return mock CI build status.

    Args:
        repo: Repository name (e.g. "backend-api", "frontend-app").
        branch: Branch name (e.g. "main", "dev").

    Returns:
        On success: {"success": True, "data": {"status": str, "last_run": str,
                     "duration_s": int, "error"?: str}}
        On miss:    {"success": False, "error": str}
    """
    mock_data = {
        ("backend-api", "main"): {"status": "passing", "last_run": "2026-07-28T10:00:00Z", "duration_s": 245},
        ("backend-api", "dev"): {"status": "failing", "last_run": "2026-07-28T09:30:00Z", "duration_s": 180, "error": "3 test failures"},
        ("frontend-app", "main"): {"status": "passing", "last_run": "2026-07-28T10:15:00Z", "duration_s": 120},
    }
    key = (repo.lower().strip(), branch.lower().strip())
    if key in mock_data:
        return {"success": True, "data": mock_data[key]}
    return {"success": False, "error": f"No build data for repo='{repo}', branch='{branch}'"}


def search_docs(query: str) -> dict:
    """Return mock documentation search results.

    Args:
        query: Free-text search string; matched word-by-word against docs.

    Returns:
        {"success": True, "data": {"query": str, "total": int,
         "results": [{"title": str, "snippet": str, "url": str}, ...]}}
    """
    all_docs = [
        {"title": "Authentication Guide", "snippet": "Use JWT tokens for API authentication. Set Authorization header with Bearer token.", "url": "/docs/auth"},
        {"title": "Database Setup", "snippet": "PostgreSQL 16 is required. Run migrations with: python manage.py migrate", "url": "/docs/database"},
        {"title": "Deployment Guide", "snippet": "Deploy using Docker. Build with: docker build -t app . and push to registry.", "url": "/docs/deploy"},
        {"title": "API Rate Limiting", "snippet": "Rate limit is 100 requests per minute per API key. Use X-RateLimit headers.", "url": "/docs/rate-limit"},
    ]
    query_lower = query.lower()
    results = [doc for doc in all_docs if any(word in doc["title"].lower() or word in doc["snippet"].lower() for word in query_lower.split())]
    return {"success": True, "data": {"query": query, "results": results, "total": len(results)}}


def create_ticket(title: str, description: str, priority: str = "medium") -> dict:
    """Create a mock ticket. This is a 'dangerous' tool that should require approval.

    Args:
        title: Ticket title.
        description: Ticket description.
        priority: One of "low", "medium", "high", "critical". Defaults to "medium".

    Returns:
        On success: {"success": True, "data": {"ticket_id": str, "title": str,
                     "description": str, "priority": str, "status": str,
                     "created_at": str}}
        On invalid priority: {"success": False, "error": str}
    """
    valid_priorities = ["low", "medium", "high", "critical"]
    if priority.lower() not in valid_priorities:
        return {"success": False, "error": f"Invalid priority '{priority}'. Must be one of: {valid_priorities}"}
    return {"success": True, "data": {"ticket_id": "TICKET-42", "title": title, "description": description, "priority": priority.lower(), "status": "open", "created_at": "2026-07-28T12:00:00Z"}}
