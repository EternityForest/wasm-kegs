import json
import os
from wasm_kegs import Plugin, packages


p = packages.PackageStore()

class VowelCountPlugin(Plugin):
    """This plugin type supports vowel counting plugins."""
    plugin_type = "kegs.testing.vowelcounter"
    
    def count_vowels(self, text):
        t= self.extism_plugin.call("count_vowels", text).decode()
        return json.loads(t)["count"]
    

class SimpleRustPlugin(Plugin):
    plugin_type = "kegs.testing.simple_rust_plugin"
    
    def greet(self, name: str)->str:
        return self.extism_plugin.call("greet", name).decode()
    

path = os.path.join(os.path.dirname(__file__), "count_vowels_plugin")
path2 = os.path.join(os.path.dirname(__file__), "simple_rust_plugin",
                     "simple-plugin-keg-folder")

def test_count_vowels():
    with p:
        plugin = VowelCountPlugin(path+":count_vowels", {})
        assert plugin.count_vowels("hello") == 2

def test_rust_plugin():
    with p:
        plugin = SimpleRustPlugin(path2+":simple_rust_plugin", {})
        assert plugin.greet("world") == "Hello, world!"