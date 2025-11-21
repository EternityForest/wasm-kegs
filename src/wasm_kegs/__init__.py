from __future__ import annotations
import os
import tomllib
import weakref
from typing import Any
import uuid
import extism

from . import packages

_plugins_by_instance_id: weakref.WeakValueDictionary[str, PluginLoader] = weakref.WeakValueDictionary()


@extism.host_fn("keg_get_static_resource")
def keg_get_static_resource(instance_id: str, path: str) -> bytes:
    plugin = _plugins_by_instance_id[instance_id]
    return open(os.path.join(plugin.plugin_folder, "static", path), "rb").read()


class PluginLoader():
    """Must subclass to get a specific plugin type."""    
    wasi = False

    plugin_type = ""

    def __init__(self,plugin: str, config=dict[str, Any]):
        p = packages.PackageStore().find_plugin(plugin)

        self.plugin_folder: str = p

        _package, plugin = packages.parse_plugin_name(plugin)

        with open(os.path.join(os.path.dirname(p), "manifest.toml"),"rb") as f:
            manifest = tomllib.load(f)

        pm = manifest["plugins"][plugin]
        if not pm["type"] == self.plugin_type:
            raise RuntimeError("Plugin type mismatch")
        
        p = os.path.join(p, "plugin.wasm")


        self.instance_id: str = str(uuid.uuid4())

        self.extism_plugin = extism.Plugin(p, wasi=self.wasi)

        if self.extism_plugin.function_exists("plugin_init"):
            self.extism_plugin.call("plugin_init", self.instance_id)

        _plugins_by_instance_id[self.instance_id] = self

