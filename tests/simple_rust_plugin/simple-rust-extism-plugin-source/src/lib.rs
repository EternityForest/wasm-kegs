use std::string;

use extism_pdk::*;

use wasm_kegs_sdk::KegsPayload;


use wasm_kegs_sdk::keg_get_static_resource;

#[host_fn("extism:host/user")]
extern "ExtismHost" {
    fn keg_test_get_name() -> String;
}


#[plugin_fn]
pub unsafe fn readback(name: String) -> FnResult<String> {
    Ok(
        String::from_utf8(
            keg_get_static_resource(name)?
    )?)
    }


#[plugin_fn]
pub unsafe fn greet(name: String) -> FnResult<String> {
    Ok(format!("Hello, {}, from {}!", name, keg_test_get_name()?))
}
