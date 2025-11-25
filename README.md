
## WebAssembly Kegs

A python packaging format for WebAssembly Extism packages.

Very early WIP.

Plugins are made directly using the extism sdk, the actual .wasm file is a standard
normal extism plugin, packaged in a folder with some metadata.

## Plugin Names

Every plugin is named "package:plugin".  All special chars besides . and _ are reserved for the plugin part.

Packages can be direct file paths starting with /, and later may be URLs as well.


## Argument and return value data encoding

Since Extism only does byte buffers, we have a very minimal packed struct encoding.
We only allow i64, f32, and bytes or strings prefixed by the length, called
pStr and pBin.

Pack together all your variables, and there's your data.

Some functions that have one argument may take and return raw strings and byte buffers with no extra framing.

We do this because we might want to reuse the framework for embedded systems,
and a full encoder would add too much code size to the .wasm


## Using Plugins

To use a plugin, you need a PluginLoader subclass for that specific
plugin type:

```python

p = packages.PackageStore()

class VowelCountPlugin(PluginLoader):
    """This plugin type supports vowel counting plugins."""
    plugin_type = "kegs.testing.vowelcounter"
    
    def count_vowels(self, text):
        t= self.extism_plugin.call("count_vowels", text).decode()
        return json.loads(t)["count"]

path = os.path.join(os.path.dirname(__file__), "count_vowels_package")

def test_count_vowels():
    with p:
        plugin = VowelCountPlugin(path+":count_vowels", {})
        assert plugin.count_vowels("hello") == 2
```

## Keg Directories

A keg plugin package contains one or more plugins.  Plugins are tightly bound
to their package, there is no expectation or support for being able to install them without their parent package, as packages may contain shared resources usable by all
plugins.

The whole thing may be packaged in a .zip with the extenion ".keg".  The root
of the zip should be the root of the keg directory, do not add an extra layer
of folder.


The plugin should be called plugin.wasm.


```
kegs-package-dir/
   manifest.toml
   static/
        # Shared static resources accessible to all plugins in the
        # Package go here.
   plugin1/
      plugin.wasm
```

Manifests contain info on the plugins

```toml
[package]
name = "rust_plugin_example"
version = "1.0.0"
description = "Example plugin showing minimal structure"
author = "Somebody"


[plugins.simple_rust_plugin]
type="kegs.testing.simple_rust_plugin"
```

## kegs-defined APIs 

```rust

// Read a file from the static dir in a plugin
#[host_fn("extism:host/user")]
extern "ExtismHost" {
    fn keg_get_static_resource(instance_id: String, path: String) -> Vec<u8>;
}


```