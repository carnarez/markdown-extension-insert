"""Make `markdown-insert` installable (via `pip install git+https://...`)."""

import setuptools  # type: ignore

setuptools.setup(
    author="carnarez",
    description="Add support for file inclusion to Python-Markdown.",
    install_requires=["markdown"],
    name="markdown-insert",
    package_data={"": ["*.pyi"]},
    py_modules=["markdown_insert"],
    url="https://github.com/carnarez/markdown-insert",
    version="0.0.1",
)
