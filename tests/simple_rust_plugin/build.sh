cd ./simple-rust-extism-plugin-source

cargo build --target wasm32-unknown-unknown
mv target/wasm32-unknown-unknown/debug/simple_rust_extism_plugin.wasm  ../simple-plugin-keg-folder/simple_rust_plugin/plugin.wasm