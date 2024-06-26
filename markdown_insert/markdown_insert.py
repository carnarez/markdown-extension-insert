"""Python-Markdown extension processing the `&[]()` insertion markers.

`pip install git+https://github.com/carnarez/markdown-insert` and refer to the brilliant
[`Python` implementation](https://github.com/Python-Markdown/markdown).

This was made to allow addition of external `Markdown` and/or HTML into the current
document. Since it is processed before any rendering happens it can be used to insert
any kind of [text] inputs; use/authorise with caution!

The marker is to be read "**insert [** *line ranges (if provided, otherwise all
lines)* **] from (** *file at this path* **)**."

Example:
-------
```markdown
This is the external snippet located in `/wherever/snippet.md`.
```
```python
import markdown
provided = '''
**Snippet:**

&[1-10](/wherever/snippet.md)

Caption of the snippet.
'''.strip()
rendered = markdown.markdown(provided, extensions=[InsertExtension()])
expected = '''
**Snippet:**

This is the external snippet located in `/wherever/snippet.md`.

Caption of the snippet.
'''.strip()
assert rendered == expected
```

Notes:
-----
* The marker needs to be on its own line, by itself. Any number of spacing character is
  allowed in front/back, but no other text.
* This implementation is rather simplistic, check
  [`markdown-include`](https://github.com/cmacmackin/markdown-include) for a more
  flexible handling of inserts (via a different syntax), or the
  [extension](https://facelessuser.github.io/pymdown-extensions/extensions/snippets/)
  from the [`pymdown` collection](https://facelessuser.github.io/pymdown-extensions/).

"""

import pathlib
import re
import sys

from markdown.core import Markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class InsertPreprocessor(Preprocessor):
    """Preprocessor to catch and replace the `&[]()` markers.

    We are here abusing the `Markdown` link syntax; we need to run it *before* the
    regular processing of the `Markdown` content.
    """

    def __init__(self, md: Markdown, config: dict[str, str] | None = None) -> None:
        """Forward the configuration of the extension.

        Parameters
        ----------
        md : markdown.core.Markdown
            The internal `Markdown` object associated with the document to render.
        config : dict[str, str]
            Dictionary of the extension configuration options. Defaults to `None`.

        Attributes
        ----------
        parent_path : str
            Path to base the inserts from (allowing relative paths in the source
            document).

        """
        super().__init__(md)
        self.parent_path = "" if config is None else config["parent_path"]

    @staticmethod
    def expand_indices(ranges: str) -> list[int]:
        """Expand a textual description of line range(s) to indices.

        Parameters
        ----------
        ranges : str
            Line indices or range(s) to include, *i.e.*, `"1-4 7-10 22"`. Note the
            **lines are indexed from 1** (to make it more human-readable).

        Returns
        -------
        : list[int]
            List of all indices to consider, 0-based for `Python`. The example from
            above would return: `[0, 1, 2, 3, 6, 7, 8, 9, 21]`.

        """
        indices: list[int] = []

        for r in ranges.strip().split():
            try:
                i, j = tuple(map(int, r.split("-")))  # check for nan
                for n in range(i - 1, j):
                    indices.append(n)
            except ValueError:
                n = int(r)  # check for nan
                indices.append(n - 1)

        return indices

    def run(self, lines: list[str]) -> list[str]:
        r"""Overwritten method to process the input `Markdown` lines.

        Parameters
        ----------
        lines : list[str]
            `Markdown` content (split by `\n`).

        Returns
        -------
        : list[str]
            Same list of lines, but processed (*e.g.*, containing the inserted content).
            The leading spacing -taken from the marker- is conserved for each inserted
            line.

        Notes
        -----
        * *One per line!*
        * The current implementation allows inserting *within triple-quoted blocks*.

        """
        extended_lines = []

        for line in lines:
            match = list(re.finditer(r"^(\s*?)&\[(.*?)\]\((.+?)\)$", line))

            if match:
                spc, rng, src = match[0].groups()
                indices = self.expand_indices(rng)

                try:
                    with pathlib.Path(f"{self.parent_path}/{src}").open() as f:
                        for i, l in enumerate(f.readlines()):
                            if not indices or i in indices:
                                extended_lines.append(f"{spc}{l.strip()}")
                except FileNotFoundError:
                    sys.stderr.write(
                        f'ERROR: "{self.parent_path}/{src}" does not exist.\n',
                    )

            else:
                extended_lines.append(line)

        return extended_lines


class InsertExtension(Extension):
    """Extension proper, to be imported when calling for the `Markdown` renderer."""

    def __init__(self, path: str = ".", **kwargs) -> None:
        """Build the configuration option dictionary.

        Attributes
        ----------
        path: str
            Extra path prefix to add when fishing for the inserted file. Defaults to
            `.`.

        """
        self.config = {"parent_path": [path, "Path to base the inserts from."]}
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown) -> None:
        """Overwritten method to process the content.

        Parameters
        ----------
        md : markdown.core.Markdown
            Internal `Markdown` object to process.

        Notes
        -----
        Since we are abusing the `Markdown` link syntax the preprocessor needs to be
        called with a high priority (100).

        """
        md.preprocessors.register(
            InsertPreprocessor(md, self.getConfigs()),
            name="insert-snippet",
            priority=100,
        )
