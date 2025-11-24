from __future__ import annotations
import os
import tomllib
import weakref
from typing import Any, Callable, TypeVar
import uuid
import extism

from . import packages

_plugins_by_instance_id: weakref.WeakValueDictionary[str, PluginLoader] = weakref.WeakValueDictionary()

def get_running_instance(plugin: extism.CurrentPlugin) -> PluginLoader:
    """If this is being called from the plugin, 
    we can find out what plugin instance

    """
    return plugin.host_context() # type: ignore


@extism.host_fn("keg_get_static_resource")
def keg_get_static_resource(current_plugin: extism.CurrentPlugin, path: str) -> bytes:
    plugin =  get_running_instance(current_plugin)
    return open(os.path.join(plugin.plugin_folder, "static", path), "rb").read()




_LoaderTypeVar = TypeVar("_LoaderTypeVar")

class PluginLoader():
    """Must subclass to get a specific plugin type."""    
    wasi = False

    plugin_type = ""


    @classmethod
    def get_running_instance(cls: type[_LoaderTypeVar], current_plugin: extism.CurrentPlugin) -> _LoaderTypeVar:
        """A host_fn can define the first param as current_plugin: extism.CurrentPlugin,
        to be passed this.

        Thia is  host_context() wrapper that checks the type.
        """
        x = current_plugin.host_context() # type: ignore
        if not isinstance(x, cls):
            raise RuntimeError(f"Plugin type mismatch, got {type(x)} but expected {cls}")
        return x


    def call_plugin(self, name: str, data: Any) -> bytes:
        """Helper to make sure we always call with the right context"""
        return self.extism_plugin.call(name, data, host_context=self)
    
    
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
            self.call_plugin("plugin_init", b'')

        _plugins_by_instance_id[self.instance_id] = self

