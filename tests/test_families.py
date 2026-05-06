import re

from repo_review.families import (
    Family,
    get_family_description,
    get_family_name,
    sort_family_keys,
)
from repo_review.html import to_html


def test_getters():
    families = {"general": Family({"name": "General", "description": "General checks"})}

    assert get_family_description(families, "general") == "General checks"
    assert get_family_name(families, "general") == "General"

    assert get_family_description(families, "unknown") == ""
    assert get_family_name(families, "unknown") == "unknown"


def test_family_sorting_in_html():
    """Test that families are sorted by order value, then alphabetically."""
    families = {
        "validate-pyproject": Family(
            {
                "name": "Validate-PyProject",
                "order": 0,
                "description": "Validation checks",
            }
        ),
        "general": Family(
            {"name": "General", "order": -3, "description": "General checks"}
        ),
        "pyproject": Family(
            {"name": "PyProject", "order": -2, "description": "PyProject checks"}
        ),
        "github": Family(
            {
                "name": "GitHub Actions",
                "order": 0,
                "description": "GitHub Actions checks",
            }
        ),
    }

    html = to_html(families, [])

    # Extract family names from h3 tags in the order they appear
    families_in_order = re.findall(r"<h3>(.*?)</h3>", html)

    # Expected order: by order value first (-3, -2, then 0s), then alphabetically within each order
    expected = ["General", "PyProject", "GitHub Actions", "Validate-PyProject"]
    assert families_in_order == expected


def test_sort_family_keys():
    families = {
        "validate-pyproject": Family({"order": 0}),
        "general": Family({"order": -3}),
        "pyproject": Family({"order": -2}),
        "github": Family({"order": 0}),
    }

    assert sort_family_keys(families) == [
        "general",
        "pyproject",
        "github",
        "validate-pyproject",
    ]
