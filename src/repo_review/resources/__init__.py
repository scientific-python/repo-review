from __future__ import annotations

import importlib.resources

__all__ = ["resources"]


resources = importlib.resources.files(__name__)
