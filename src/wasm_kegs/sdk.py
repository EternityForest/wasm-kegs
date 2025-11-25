# This file is only for building plugins


import shutil
import subprocess
import tomllib
import os


def rsync_dirs(source_dir, destination_dir):
    """
    Syncs the contents of a source directory to a destination directory using rsync.

    :param source_dir: The path to the source directory (must have a trailing slash for contents only).
    :param destination_dir: The path to the destination directory.
    """
    # Ensure source path has a trailing slash to copy contents *into* the destination
    if not source_dir.endswith(os.sep):
        source_dir += os.sep
    
    # The rsync command:
    # -a: archive mode (preserves permissions, ownership, timestamps, recursive)
    # -v: verbose
    # --delete: delete files in destination that are not in source (for true mirroring)
    command = [
        'rsync',
        '-av',
        '--delete',
        source_dir,
        destination_dir
    ]

    print(f"Running command: {' '.join(command)}")
    
    try:
        # Run the command
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Rsync completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Rsync failed: {e.stderr}")
    except FileNotFoundError:
        print("Error: rsync command not found. Make sure rsync is installed and in your system's PATH.")

def copy_static(path: str, keg_build_output: str):

    t = tomllib.load(open(os.path.join(path, "Cargo.toml"), "rb"))

    md = t["tools"]
    if "kegs" not in md:
        return
    
    if "static-src" not in md["kegs"]:
        return
    
    src = md["kegs"]["static-src"]
    src = os.path.join(path, src)

    if os.path.exists(src):
        os.makedirs(os.path.join((keg_build_output), "static"), exist_ok=True)
        rsync_dirs(src, os.path.join(keg_build_output, "static"))

def build_rust_plugin(workspace: str, path: str, plugin_dest: str):

    t = tomllib.load(open(os.path.join(path, "Cargo.toml"), "rb"))
    rust_name = t["package"]["name"].replace("-", "_")

    kegs_plugin_name = t["tools"]["kegs"]["plugin-name"]


    rust_build_output = os.path.join(workspace, "target", "wasm32-unknown-unknown", "debug", rust_name + ".wasm")
    subprocess.check_call(["cargo", "build", "--target", "wasm32-unknown-unknown"], cwd=path)

    os.makedirs(os.path.join(plugin_dest, kegs_plugin_name), exist_ok=True)
    shutil.copyfile(rust_build_output, os.path.join(plugin_dest, kegs_plugin_name,"plugin.wasm"))



def build_rust_package(workspace_path: str):
    t = tomllib.load(open(os.path.join(workspace_path, "Cargo.toml"), "rb"))

    md = t["tools"]

    keg_dest = os.path.join(workspace_path, "kegs-build", md["kegs"]["package-name"])
    print(f"Building keg package to {keg_dest}")
    manifest_src = md["kegs"]["manifest-src"]
    manifest_src = os.path.join(workspace_path, manifest_src)

    os.makedirs(keg_dest, exist_ok=True)
    shutil.copyfile(manifest_src, os.path.join(keg_dest, "manifest.toml"))

    for i in md["kegs"]["plugins"]:
        path = os.path.join(workspace_path, i)
        build_rust_plugin(workspace_path, path, keg_dest)

    copy_static(workspace_path, keg_dest)
    shutil.copy


if __name__ == "__main__":
    build_rust_package(os.getcwd())