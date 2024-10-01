# 'Compile' template files into Terraform configuration files.
# There isn't anything actually Terraform specific in the code.
# Pass in any source and output directory and any files with a '.j2' extension
# will be rendered as templates, and anything else will be copied as is.
#
# Usage:
#   python compile-terraform.py <source_dir> <output_dir>

from collections.abc import Callable
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from os import path, makedirs
from shutil import copy2
from sys import argv


def compile_terraform(source_dir: str, output_dir: str) -> None:
    env = Environment(
        loader = FileSystemLoader(source_dir),
        autoescape = select_autoescape()
    )

    # 'Compile' any file with a '.j2' extension.
    is_compilable = filter_by_extension(".j2")

    for source_file_name in env.list_templates():
        source_file_name: str

        if is_compilable(source_file_name):
            print(f"Compiling: {source_file_name}")
            compile_file(env, source_dir, source_file_name, output_dir)
        else:
            print(f"Copying: {source_file_name}")
            copy_file(source_dir, source_file_name, output_dir)


def compile_file(
        env: Environment,
        source_dir: str,
        source_file_name: str,
        output_dir: str) -> None:

    source_file_path = path.join(source_dir, source_file_name)
    newline = end_of_line_sequence(source_file_path)

    # [:-3] to remove assumed '.j2' extension
    output_file_path = path.join(output_dir, source_file_name)[:-3]
    ensure_file_parent_dir_exists(output_file_path)

    template: Template = env.get_template(source_file_name)
    compiled = template.render().strip()
    if len(compiled) > 0:
        compiled += newline
    with open(output_file_path, "w", newline=newline) as f:
        f.write(compiled)


def copy_file(source_dir: str, source_file_name: str, output_dir: str) -> None:
    source_file_path = path.join(source_dir, source_file_name)
    output_file_path = path.join(output_dir, source_file_name)
    ensure_file_parent_dir_exists(output_file_path)
    copy2(source_file_path, output_file_path)


def ensure_file_parent_dir_exists(file_path: str) -> None:
    file_parent_dir = path.split(file_path)[0]
    ensure_dir_exists(file_parent_dir)


def ensure_dir_exists(dir_path: str) -> None:
    if not path.exists(dir_path):
        makedirs(dir_path)


def filter_by_extension(extension: str | list[str]) -> Callable[[str], bool]:
    extensions_list = [extension] if extension is str else extension
    def filter(input_path: str) -> bool:
        return any(
            input_path.endswith(extension) for extension in extensions_list)
    return filter


def end_of_line_sequence(file_path: str) -> str:
    # A somewhat naive implementation that assumes the first used end of line
    # sequence is the same one used throughout the file.
    # A slower alternative could be to read the whole file and assume the most
    # frequently used end of line sequence is the intended one for the file.
    print(file_path)
    with open(file_path, 'rb') as f:
        # Assume source code doesn't have ridiculously long lines so a line
        # break expected to occur in first 200 characters
        bytes = f.read(200)
        first_new_line_byte = next(
            filter(lambda byte: byte in (10, 13), bytes),
            None)
        if first_new_line_byte == 13:
            # Assume if we've found CR it will be followed by LF, and
            # it is never going to be old Mac CR only new line character.
            return "\r\n"

        # Otherwise LF or line end not found, so use LF
        return "\n"


def show_usage() -> None:
    print("Usage:")
    print("    python compile-terraform.py <source_dir> <output_dir>")


if __name__ == "__main__":
    if (len(argv) < 3):
        show_usage()
        exit(1)

    compile_terraform(argv[1], argv[2])
