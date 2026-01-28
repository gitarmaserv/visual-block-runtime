"""Plugin loader for discovering and loading plugins."""
import importlib.util
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any


class PluginLoader:
    """Loads plugins from the plugins directory."""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self._plugins: Dict[str, Dict[str, Any]] = {}
    
    def discover_plugins(self) -> List[Dict]:
        """Discover and load all plugins from the plugins directory."""
        self._plugins = {}
        
        if not self.plugins_dir.exists():
            return []
        
        for plugin_id in os.listdir(self.plugins_dir):
            plugin_path = self.plugins_dir / plugin_id
            plugin_file = plugin_path / "plugin.py"
            
            if not plugin_file.exists():
                continue
            
            try:
                plugin = self._load_plugin(plugin_id, plugin_file)
                if plugin:
                    self._plugins[plugin_id] = plugin
            except Exception as e:
                print(f"Error loading plugin {plugin_id}: {e}")
                continue
        
        return list(self._plugins.values())
    
    def _load_plugin(self, plugin_id: str, plugin_file: Path) -> Optional[Dict]:
        """Load a single plugin from its module."""
        spec = importlib.util.spec_from_file_location(plugin_id, plugin_file)
        if spec is None or spec.loader is None:
            return None
        
        module = importlib.util.module_from_spec(spec)
        
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"Error executing module {plugin_id}: {e}")
            return None
        
        # Get spec and run functions
        get_spec = getattr(module, 'get_spec', None)
        run = getattr(module, 'run', None)
        
        if get_spec is None:
            print(f"Plugin {plugin_id} missing get_spec() function")
            return None
        
        try:
            spec_data = get_spec()
        except Exception as e:
            print(f"Error calling get_spec() for {plugin_id}: {e}")
            return None
        
        # Validate spec
        if not isinstance(spec_data, dict):
            print(f"Plugin {plugin_id} get_spec() must return a dict")
            return None
        
        required_fields = ["plugin_id", "name", "version", "description", "category"]
        for field in required_fields:
            if field not in spec_data:
                print(f"Plugin {plugin_id} spec missing required field: {field}")
                return None
        
        # Validate spec.plugin_id matches directory name
        if spec_data["plugin_id"] != plugin_id:
            print(f"Plugin {plugin_id} spec.plugin_id mismatch")
            return None
        
        return {
            "plugin_id": plugin_id,
            "name": spec_data["name"],
            "version": spec_data["version"],
            "description": spec_data["description"],
            "category": spec_data.get("category", "Other"),
            "tags": spec_data.get("tags", []),
            "requires_input": spec_data.get("requires_input", False),
            "produces_output": spec_data.get("produces_output", False),
            "params": spec_data.get("params", []),
            "spec": spec_data,
            "run_func": run
        }
    
    def get_plugin(self, plugin_id: str) -> Optional[Dict]:
        """Get a loaded plugin by ID."""
        return self._plugins.get(plugin_id)
    
    def get_all_plugins(self) -> List[Dict]:
        """Get all loaded plugins."""
        return list(self._plugins.values())
    
    def get_plugins_by_category(self) -> Dict[str, List[Dict]]:
        """Group plugins by category."""
        by_category = {}
        for plugin in self._plugins.values():
            category = plugin.get("category", "Other")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(plugin)
        return by_category


# Global plugin loader instance
_plugin_loader: Optional[PluginLoader] = None


def get_plugin_loader() -> PluginLoader:
    """Get or create the global plugin loader."""
    global _plugin_loader
    if _plugin_loader is None:
        _plugin_loader = PluginLoader()
    return _plugin_loader


def load_plugins(plugins_dir: str = None) -> List[Dict]:
    """Load all plugins and return their specs."""
    loader = get_plugin_loader()
    if plugins_dir:
        loader.plugins_dir = Path(plugins_dir)
    return loader.discover_plugins()
