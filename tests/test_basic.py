import json
import os

import extism
from wasm_kegs import PluginLoader, packages
import wasm_kegs


p = packages.PackageStore()

class VowelCountPlugin(PluginLoader):
    """This plugin type supports vowel counting plugins."""
    plugin_type = "kegs.testing.vowelcounter"
    
    def count_vowels(self, text):
        t= self.extism_plugin.call("count_vowels", text).decode()
        return json.loads(t)["count"]
    



@extism.host_fn("keg_test_get_name")
def get_name(plugin: extism.CurrentPlugin)->str:
    p = SimpleRustPlugin.get_running_instance(plugin)
    return p.name

class SimpleRustPlugin(PluginLoader):
    plugin_type = "kegs.testing.simple_rust_plugin"

    def __init__(self, plugin: str, config):
        super().__init__(plugin, config)
        self.name = "Ken"
    
    def greet(self, name: str)->str:
        return self.call_plugin("greet", name).decode()
    
    def read_static_resource(self, path: str)->str:
        return self.call_plugin("readback", path).decode()
    

path = os.path.join(os.path.dirname(__file__), "count_vowels_package")
path2 = os.path.join(os.path.dirname(__file__), "simple_rust_plugin",
                     "simple-plugin-keg-folder")

def test_count_vowels():
    with p:
        plugin = VowelCountPlugin(path+":count_vowels", {})
        assert plugin.count_vowels("hello") == 2

def test_rust_plugin():
    with p:
        plugin = SimpleRustPlugin(path2+":simple_rust_plugin", {})
        assert plugin.greet("world") == "Hello, world, from Ken!"

        assert plugin.read_static_resource("hello.txt") == "test"
