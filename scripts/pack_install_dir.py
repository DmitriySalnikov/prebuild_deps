import argparse, re, os, subprocess, io, hashlib
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("root", help="Install directory")
parser.add_argument("-c", "--check", action="store_true", required=False)
parser.add_argument("--no_pack", action="store_true", required=False)
args = parser.parse_args()

pack_dir = os.path.abspath(args.root).replace("\\", "/").removesuffix("/")
pack_name = os.path.basename(pack_dir)
script_dir = os.path.abspath(os.path.dirname(__file__))
prebuild_dir = os.path.join(script_dir, "..", "prebuild")

if pack_name == "install":
    pack_name = os.path.basename(os.path.dirname(pack_dir))

print(f"Pack name: {pack_name}")
print(f"Working directory: {pack_dir}")
print(f"Prebuild directory: {prebuild_dir}")
print()


def fix_absolute_paths():
    search_root = re.compile(pack_dir.replace("/", r"[\\\/]").replace(":", r"\:"))
    search_external = re.compile(r"(\")(.*[\\\/]deps[\\\/]external[\\\/][\w\s\d\-\_]*)(.*\")")
    search_import_prefix = re.compile(r"\$\{_IMPORT_PREFIX\}")

    def get_cd_backwards(file_path, root_path) -> str:
        trailing_path = file_path.replace(root_path, "")
        cd_backward = "/".join([".."] * trailing_path.count("/"))
        if trailing_path.count("/"):
            cd_backward = "/" + cd_backward
        return cd_backward

    for cmake_file in Path(pack_dir).rglob("*.cmake"):
        content = cmake_file.read_text(encoding="utf-8")
        cmake_file_path = cmake_file.absolute().as_posix()

        install_dir = "${OBSNOTIF_DEPS_INSTALL_DIR}"

        new_content, count_root = search_root.subn(install_dir, content)
        new_content, count_import = search_import_prefix.subn(install_dir, new_content)
        new_content, count_external = search_external.subn(
            lambda m: f"{m.group(1)}{install_dir}{m.group(3)}", new_content
        )

        count = count_root + count_import + count_external
        if count:
            print(
                f"{cmake_file_path.replace(pack_dir, "")}: {count} replacements. Root: {count_root}, IMPORT_PREFIX: {count_import}, External dir: {count_external}"
            )

        if count and not args.check:
            cmake_file.write_text(new_content, encoding="utf-8")

    for pc_file in Path(pack_dir).rglob("*.pc"):
        content = pc_file.read_text(encoding="utf-8")
        pc_file_path = pc_file.absolute().as_posix()

        cd_backward = get_cd_backwards(os.path.dirname(pc_file_path), pack_dir)
        install_dir = f"${{pcfiledir}}{cd_backward}"

        new_content, count = search_root.subn(install_dir, content)
        if count:
            print(f"{pc_file_path.replace(pack_dir, "")}: {count} replacements.")

        if count and not args.check:
            pc_file.write_text(new_content, encoding="utf-8")


def make_archive():
    global pack_name
    os.makedirs(prebuild_dir, exist_ok=True)
    zip_file = os.path.join(prebuild_dir, pack_name + ".7z")

    if os.path.exists(zip_file):
        os.remove(zip_file)

    cpus = os.cpu_count()
    cpus = 1 if cpus == None else cpus
    subprocess.run(["7z", "a", zip_file, "-bd", f"-mmt{max(cpus - 2, 1)}", "-mx7"], cwd=pack_dir)


fix_absolute_paths()

if not args.no_pack:
    print()
    make_archive()
