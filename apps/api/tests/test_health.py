from careos_api import urls


def test_health_route_is_registered() -> None:
    patterns = {str(pattern.pattern) for pattern in urls.urlpatterns}
    assert "health/" in patterns
