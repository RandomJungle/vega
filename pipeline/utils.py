# coding=utf-8
from typing import List

from spacy.tokens.span import Span


def remove_tokens_custom_attributes(spans: List[Span]):
    """
    Remove all custom attributes extensions on tokens from a sequence of spans
    Args:
        spans: Sequence of spans to process
    Returns:
        function modifying its parameters
    """
    for span in spans:
        for token in span:
            for extension in token._._extensions.keys():
                token._.set(extension, False)
