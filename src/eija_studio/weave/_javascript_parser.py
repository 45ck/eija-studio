"""Native imports for the isolated JavaScript worker; never import from Studio."""

import tree_sitter_javascript
from tree_sitter import Language, Parser


def create_parser() -> Parser:
    """Construct the pinned grammar's parser without loading any target module."""
    return Parser(Language(tree_sitter_javascript.language()))
