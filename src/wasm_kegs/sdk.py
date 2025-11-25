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
    
    if "static_src" not in md["kegs"]:
        return
    
    src = md["kegs"]["static_src"]
    src = os.path.join(path, src)

    if os.path.exists(src):
        os.makedirs(os.path.join((keg_build_output), "static"), exist_ok=True)
        rsync_dirs(src, os.path.join(keg_build_output, "static"))

def build_rust_plugin(path: str, keg_dest: str):

    t = tomllib.load(open(os.path.join(path, "Cargo.toml"), "rb"))
    rust_name = t["package"]["name"]

    kegs_plugin_name = t["tools"]["kegs"]["plugin_name"]


    rust_build_output = os.path.join(path, "target", "wasm32-unknown-unknown", "release", rust_name + ".wasm")
    subprocess.check_call(["cargo", "build", "--release", "--target", "wasm32-unknown-unknown"], cwd=path)

    shutil.copyfile(rust_build_output, os.path.join(keg_dest, kegs_plugin_name,"plugin.wasm"))



def build_rust_package(workspace_path: str):
    t = tomllib.load(open(os.path.join(workspace_path, "Cargo.toml"), "rb"))

    md = t["tools"]

    keg_dest = os.path.join(workspace_path, md["kegs"]["package_name"])

    for i in md["kegs"]["plugins"]:
        path = os.path.join(workspace_path, i)
        keg_dest = os.path.join(workspace_path, "kegs", i)
        os.makedirs(keg_dest, exist_ok=True)
        build_rust_plugin(path, keg_dest)

    copy_static(workspace_path, keg_dest)


if __name__ == "__main__":
    build_rust_package(".")