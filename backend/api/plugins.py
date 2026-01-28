"""API routes for plugins."""
from fastapi import APIRouter
from backend.plugins.loader import load_plugins, get_plugin_loader

router = APIRouter(prefix="/plugins", tags=["plugins"])


@router.get("")
def get_plugins():
    """Get list of available plugins."""
    plugins = load_plugins()
    return {
        "plugins": [
            {
                "plugin_id": p["plugin_id"],
                "name": p["name"],
                "version": p["version"],
                "category": p["category"],
                "tags": p["tags"],
                "spec": p["spec"]
            }
            for p in plugins
        ]
    }


@router.get("/categories")
def get_plugins_by_category():
    """Get plugins grouped by category."""
    loader = get_plugin_loader()
    by_category = loader.get_plugins_by_category()
    return {
        "categories": [
            {
                "name": cat,
                "plugins": [
                    {
                        "plugin_id": p["plugin_id"],
                        "name": p["name"],
                        "version": p["version"],
                        "description": p["description"],
                        "category": p["category"],
                        "tags": p["tags"],
                        "requires_input": p["requires_input"],
                        "produces_output": p["produces_output"]
                    }
                    for p in plugins
                ]
            }
            for cat, plugins in by_category.items()
        ]
    }
