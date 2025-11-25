import json
import os
from typing import Any

import extism
from wasm_kegs import PluginLoader, packages, Payload


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

    def add(self, a: int, b: int)->int:
        p = Payload(b"")
        p.write_i64(a)
        p.write_i64(b)

        r = self.call_plugin("add_test",p.data)
        pr = Payload(r)
        return pr.read_i64()
    

path = os.path.join(os.path.dirname(__file__), "count_vowels_package")
path2 = os.path.join(os.path.dirname(os.path.dirname(__file__)), "kegs-build", "simple-rust-kegs-demo")

def test_count_vowels():
    with p:
        cfg: dict[str, Any] = {}
        plugin = VowelCountPlugin(path+":count_vowels", cfg)
        assert plugin.count_vowels("hello") == 2

def test_rust_plugin():
    with p:
        plugin = SimpleRustPlugin(path2+":simple-rust-plugin", {})
        assert plugin.greet("world") == "Hello, world, from Ken!"

        assert plugin.read_static_resource("hello.txt") == "test"


def test_rust_plugin_payload_encoding():
    with p:
        plugin = SimpleRustPlugin(path2+":simple-rust-plugin", {})

        x = Payload(b"")
        a =56567
        b = 7654

        x.write_i64(a)
        x.write_i64(b)


        assert plugin.greet("world") == "Hello, world, from Ken!"

        assert plugin.read_static_resource("hello.txt") == "test"
