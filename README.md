

## Keg Directories

A keg plugin package contains one or more plugins.

```
kegs-package-dir/
   manifest.toml
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