import os
import tomllib
from typing import Any, Callable
import extism

from . import packages

class Plugin():
    """Must subclass to get a specific plugin type."""

    host_functions: list[Callable] = []
    
    wasi = False

    plugin_type = ""

    def __init__(self,plugin: str, config=dict[str, Any]):
        p = packages.PackageStore().find_plugin(plugin)

        _package, plugin = packages.parse_plugin_name(plugin)

        with open(os.path.join(os.path.dirname(p), "manifest.toml"),"rb") as f:
            manifest = tomllib.load(f)

        pm = manifest["plugins"][plugin]
        if not pm["type"] == self.plugin_type:
            raise RuntimeError("Plugin type mismatch")
        
        p = os.path.join(p, "plugin.wasm")

        functions = list(self.host_functions)

        self.extism_plugin = extism.Plugin(p, functions=functions, wasi=self.wasi)
