import typing

from markdown.core import Markdown as Markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

class InsertPreprocessor(Preprocessor):
    @staticmethod
    def expand_indices(ranges: str) -> typing.List[int]: ...
    def run(self, lines: typing.List[str]) -> typing.List[str]: ...

class InsertExtension(Extension):
    def extendMarkdown(self, md: Markdown): ...
