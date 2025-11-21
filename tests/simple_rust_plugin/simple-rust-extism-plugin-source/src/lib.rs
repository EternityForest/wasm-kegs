use std::sync::OnceLock;
use std::string;

use extism_pdk::*;

// Store the instance id they give us in this handy container
// rust gives us for stuff that gets initialized exactly once
struct InstanceData {
    instance_id: String,
}

static INSTANCE: OnceLock<InstanceData> = OnceLock::new();


#[host_fn("extism:host/user")]
extern "ExtismHost" {
    fn keg_get_static_resource(instance_id: String, path: String) -> Vec<u8>;
}

#[plugin_fn]
pub unsafe fn readback(name: String) -> FnResult<String> {
    Ok(
        
        String::from_utf8(
            keg_get_static_resource(
                INSTANCE.get().unwrap().instance_id.clone()
            , name)?
    )?)
    }


#[plugin_fn]
pub fn greet(name: String) -> FnResult<String> {
    Ok(format!("Hello, {}, from {}!", name,INSTANCE.get().unwrap().instance_id))
}

#[plugin_fn]
pub fn plugin_init(name: String) -> FnResult<()> {
    INSTANCE.set(InstanceData { instance_id: name });
    Ok(())
}