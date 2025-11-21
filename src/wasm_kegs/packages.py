import os
import zipfile
import threading

_local = threading.local()

def get_package_store():
    if not hasattr(_local, "store"):
        raise RuntimeError("PackageStore not in use")
    if not _local.store:
        raise RuntimeError("PackageStore not in use")
    return _local.store


def parse_plugin_name(plugin:str)->tuple[str, str]:
    x = plugin.split(":")

    plugin = x[-1]
    package = ":".join(x[:-1])

    return package, plugin

class PackageStore():
    def __init__(self, path:str="~/.local/share/wasm-kegs/packages"):
        """Path must be the package store directory"""
        self.path = os.path.expanduser(path)
        os.makedirs(self.path, exist_ok=True)

    def __enter__(self):
        if  hasattr(_local, "store") and _local.store:
            raise RuntimeError("PackageStore already in use")
        _local.store = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        _local.store = None

    def ensure_package(self, package:str)->str:
        if os.path.isdir(package):
            return package
        
        if package.endswith(".keg"):
            path = os.path.join(self.path, package[:-4])

            zipfile.ZipFile(package).extractall(path)
            return path

        raise RuntimeError(f"Could not find package {package}")
        
    def find_plugin(self,plugin)->str:
        package, plugin = parse_plugin_name(plugin)
        packagedir = self.ensure_package(package)
        return os.path.join(packagedir, plugin)