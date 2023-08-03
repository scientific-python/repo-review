from repo_review.families import Family, get_family_description, get_family_name


def test_getters():
    families = {"general": Family({"name": "General", "description": "General checks"})}

    assert get_family_description(families, "general") == "General checks"
    assert get_family_name(families, "general") == "General"

    assert get_family_description(families, "unknown") == ""
    assert get_family_name(families, "unknown") == "unknown"
