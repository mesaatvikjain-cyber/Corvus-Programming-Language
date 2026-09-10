#!/usr/bin/env python3
"""
Corvus Package Manager (CPM) CLI Tool
Version: 1.0.0
Author: Saatvik Jain (Creator of Corvus)
"""

import sys
import os
import json
import shutil
import urllib.request
import zipfile
import subprocess
import tempfile
import re
from urllib.parse import urlparse, urlunparse


def build_validated_github_zip_url(base_url: str) -> str:
    try:
        # Minimal path validation
        if "/../" in base_url or re.search(r"/%2e%2e/", base_url, re.IGNORECASE):
            raise ValueError("Invalid path")
        
        parsed = urlparse(base_url)
        
        # Protocol + host checks
        if parsed.scheme not in ("http", "https"):
            raise ValueError("Invalid protocol")
        if not parsed.hostname:
            raise ValueError("Invalid host")
        allowed_domains = ["github.com"]
        if parsed.hostname.lower() not in allowed_domains:
            raise ValueError("Invalid host")
        
        # Rebuild path with fixed suffix
        base_path = parsed.path.rstrip("/")
        parsed = parsed._replace(path=f"{base_path}/archive/refs/heads/main.zip")
        
        return urlunparse(parsed)
    except Exception:
        raise ValueError("Invalid URL")


CPM_VERSION = "1.0.0"
GLOBAL_PKG_DIR = os.path.expanduser(os.path.join("~", ".corvus", "packages"))


def print_banner():
    print(r"""
   ____ _____  __  ___
  / ___|  _  \/  |/  /  Corvus Package Manager (CPM)
 / /___| |_| / /|_/ /   v1.0.0
 \____/|  __/ /  / /    Package & Dependency Management for Corvus
       |_|  |_/  /_/    Created by Saatvik Jain
""")


def get_project_dir():
    return os.getcwd()


def get_manifest_path():
    return os.path.join(get_project_dir(), "corvus.json")


def load_manifest():
    path = get_manifest_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_manifest(manifest):
    path = get_manifest_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)


def cmd_init():
    print_banner()
    path = get_manifest_path()
    if os.path.exists(path):
        print(f"[!] 'corvus.json' already exists in {get_project_dir()}")
        return

    folder_name = os.path.basename(get_project_dir()) or "corvus-project"
    print("[+] Initializing new Corvus package manifest...")

    try:
        name = input(f"Package name ({folder_name}): ").strip() or folder_name
        version = input("Version (1.0.0): ").strip() or "1.0.0"
        description = input("Description: ").strip() or "A Corvus language package"
        main_file = input("Main entry file (main.crv): ").strip() or "main.crv"
        author = input("Author (Saatvik Jain): ").strip() or "Saatvik Jain"
    except (KeyboardInterrupt, EOFError):
        print("\n[!] Initialization cancelled.")
        return

    manifest = {
        "name": name,
        "version": version,
        "description": description,
        "main": main_file,
        "author": author,
        "dependencies": {}
    }

    save_manifest(manifest)
    print(f"[SUCCESS] Created 'corvus.json' in {get_project_dir()}")

    # Ensure main entry file exists
    main_path = os.path.join(get_project_dir(), main_file)
    if not os.path.exists(main_path):
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(f'# Corvus Package: {name}\n# Main entry point\n\nset str; pkg_name = "{name}"\n')
        print(f"[SUCCESS] Generated entry file '{main_file}'")


def cmd_install(args):
    target = None
    is_global = False

    for arg in args:
        if arg in ("-g", "--global"):
            is_global = True
        elif not arg.startswith("-"):
            target = arg

    dest_dir = GLOBAL_PKG_DIR if is_global else os.path.join(get_project_dir(), "corvus_modules")
    os.makedirs(dest_dir, exist_ok=True)

    if not target:
        # Install all from corvus.json
        manifest = load_manifest()
        if not manifest or "dependencies" not in manifest or not manifest["dependencies"]:
            print("[INFO] No dependencies found in 'corvus.json'. Nothing to install.")
            return
        
        print(f"[+] Installing dependencies from 'corvus.json' into '{dest_dir}'...")
        for pkg_name, pkg_source in manifest["dependencies"].items():
            _install_single(pkg_name, pkg_source, dest_dir)
        print("[SUCCESS] All dependencies installed successfully.")
        return

    # Install specific target
    pkg_name, pkg_source = _parse_target(target)
    print(f"[+] Installing '{pkg_name}' from '{pkg_source}' into '{dest_dir}'...")
    _install_single(pkg_name, pkg_source, dest_dir)

    # Record in corvus.json if local project
    if not is_global:
        manifest = load_manifest()
        if manifest is not None:
            if "dependencies" not in manifest:
                manifest["dependencies"] = {}
            manifest["dependencies"][pkg_name] = pkg_source
            save_manifest(manifest)
            print(f"[+] Added '{pkg_name}' to 'corvus.json' dependencies.")

    print(f"[SUCCESS] Package '{pkg_name}' installed successfully!")


def _parse_target(target):
    # Case 1: GitHub user/repo format (e.g. mesaatvikjain-cyber/corvus-utils)
    if "/" in target and not os.path.exists(target) and not target.startswith("http"):
        parts = target.split("/")
        pkg_name = parts[-1].replace(".git", "")
        return pkg_name, f"https://github.com/{target}"
    
    # Case 2: Local folder
    if os.path.isdir(target):
        pkg_name = os.path.basename(os.path.abspath(target))
        return pkg_name, os.path.abspath(target)
    
    # Case 3: Direct URL
    if target.startswith("http://") or target.startswith("https://"):
        pkg_name = target.split("/")[-1].split(".")[0]
        return pkg_name, target

    # Default name fallback
    return target, f"https://github.com/corvus-lang/{target}"


def _install_single(pkg_name, pkg_source, dest_dir):
    target_path = os.path.join(dest_dir, pkg_name)
    if os.path.exists(target_path):
        shutil.rmtree(target_path)

    # 1. Local folder copy
    if os.path.isdir(pkg_source):
        shutil.copytree(pkg_source, target_path)
        return

    # 2. GitHub / Web URL download
    if pkg_source.startswith("http"):
        # Check if git is available for cloning
        if pkg_source.endswith(".git") or "github.com" in pkg_source:
            zip_url = build_validated_github_zip_url(pkg_source.rstrip("/"))
            try:
                with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_zip:
                    tmp_zip_path = tmp_zip.name
                
                print(f"    Downloading {zip_url}...")
                urllib.request.urlretrieve(zip_url, tmp_zip_path)
                
                with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
                    extract_tmp = tempfile.mkdtemp()
                    zip_ref.extractall(extract_tmp)
                    extracted_folders = os.listdir(extract_tmp)
                    if extracted_folders:
                        src_folder = os.path.join(extract_tmp, extracted_folders[0])
                        shutil.move(src_folder, target_path)
                    shutil.rmtree(extract_tmp)
                os.remove(tmp_zip_path)
                return
            except Exception as e:
                print(f"    [!] Direct zip download failed ({e}), falling back to git clone...")
                subprocess.run(["git", "clone", "--depth", "1", pkg_source, target_path], check=True)
                return

    # Fallback git clone
    subprocess.run(["git", "clone", "--depth", "1", pkg_source, target_path], check=True)


def cmd_list():
    print_banner()
    local_dir = os.path.join(get_project_dir(), "corvus_modules")
    print(f"Local packages ({local_dir}):")
    _print_packages(local_dir)

    print(f"\nGlobal packages ({GLOBAL_PKG_DIR}):")
    _print_packages(GLOBAL_PKG_DIR)


def _print_packages(pkg_dir):
    if not os.path.exists(pkg_dir) or not os.listdir(pkg_dir):
        print("  (None installed)")
        return

    for item in os.listdir(pkg_dir):
        item_path = os.path.join(pkg_dir, item)
        if os.path.isdir(item_path):
            manifest_path = os.path.join(item_path, "corvus.json")
            ver = "1.0.0"
            desc = ""
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        ver = data.get("version", "1.0.0")
                        desc = f"- {data.get('description', '')}"
                except Exception:
                    pass
            print(f"  * {item} (v{ver}) {desc}")


def cmd_remove(args):
    if not args:
        print("[!] Usage: cpm remove <package_name>")
        return

    pkg_name = args[0]
    local_path = os.path.join(get_project_dir(), "corvus_modules", pkg_name)

    if os.path.exists(local_path):
        shutil.rmtree(local_path)
        print(f"[+] Removed '{pkg_name}' from 'corvus_modules/'.")
    else:
        print(f"[!] Package '{pkg_name}' not found in 'corvus_modules/'.")

    manifest = load_manifest()
    if manifest and "dependencies" in manifest and pkg_name in manifest["dependencies"]:
        del manifest["dependencies"][pkg_name]
        save_manifest(manifest)
        print(f"[+] Removed '{pkg_name}' from 'corvus.json'.")


def cmd_help():
    print_banner()
    print("""
Usage: cpm <command> [options]

Commands:
  init                     Interactively initialize a new 'corvus.json' project manifest.
  install                  Install all dependencies listed in 'corvus.json'.
  install <package>        Install a package from GitHub repo, URL, or local path.
                           Options: -g, --global  (Install into global ~/.corvus/packages)
  list                     Display installed local and global packages.
  remove <package>         Uninstall a package and remove it from 'corvus.json'.
  version                  Show CPM version.
  help                     Show this help message.

Examples:
  cpm init
  cpm install mesaatvikjain-cyber/math_extra
  cpm install ./my_local_lib
  cpm install -g mesaatvikjain-cyber/http_utils
  cpm list
  cpm remove math_extra
""")


def main():
    if len(sys.argv) < 2:
        cmd_help()
        return

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    if cmd == "init":
        cmd_init()
    elif cmd in ("install", "i"):
        cmd_install(args)
    elif cmd in ("list", "ls"):
        cmd_list()
    elif cmd in ("remove", "rm", "uninstall"):
        cmd_remove(args)
    elif cmd in ("version", "-v", "--version"):
        print(f"CPM (Corvus Package Manager) v{CPM_VERSION}")
    else:
        cmd_help()


if __name__ == "__main__":
    main()
