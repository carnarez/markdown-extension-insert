"""Make `markdown-insert` installable (via `pip install git+https://...`)."""

import setuptools  # type: ignore

setuptools.setup(
    author="carnarez",
    description="Add support for file inclusion to Python-Markdown.",
    install_requires=["markdown"],
    name="markdown-insert",
    packages=["markdown_insert"],
    package_data={"markdown_insert": ["*.pyi", "py.typed"]},
    url="https://github.com/carnarez/markdown-insert",
    version="0.0.1",
)
