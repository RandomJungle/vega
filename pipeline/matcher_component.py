# coding: utf8

import logging

from spacy.matcher.matcher import Matcher
from spacy.tokens import Doc, Span, Token


class MatcherComponent(object):
    """Matcher-based pipeline component

    Note:
        optional merging of matched spans, provided in utils class
        are function that allow to control match type (all, overlapping, etc.)
    """

    def __init__(self, nlp: Doc, component_name: str, is_attribute: str, has_attribute: str,
                 matcher, merge_on_match: bool = True):
        """Constructor of MatcherComponent object

        Args:
            nlp (Doc): Spacy Doc object
            component_name (str): Unique name of this component
            is_attribute (str): label to add for custom attribute at Token level
            has_attribute (str): label to add for custom attribute at Doc / Span level
            matcher (Matcher): matcher object to call, can be a PhraseMatcher or a Matcher
            merge_on_match (Bool): optional merging on match option, default to True
        """
        self.nlp = nlp
        self.name = component_name
        self.matcher = matcher
        self.is_attribute = is_attribute
        self.has_attribute = has_attribute
        self.merge_on_match = merge_on_match

        # Register attribute on the Token
        Token.set_extension(self.is_attribute, default=False, force=True)
        # Register attributes on Doc and Span via a getter function
        Doc.set_extension(self.has_attribute, getter=self.get_attribute, force=True)
        Span.set_extension(self.has_attribute, getter=self.get_attribute, force=True)

    def __call__(self, doc):
        """
        Apply the pipeline component on a Doc object and modify it if matches
        are found. Return the Doc, so it can be processed by the next component
        in the pipeline, if available.
        :param doc: the doc object
        :return: doc: the doc object modified
        """
        matches = self.matcher(doc)
        if matches:
            if self.merge_on_match:
                with doc.retokenize() as retokenizer:
                    for _, start, end in matches:
                        entity = Span(doc, start, end)
                        for token in entity:
                            token._.set(self.is_attribute, True)
                        retokenizer.merge(entity)
            else:
                for _, start, end in matches:
                    entity = Span(doc, start, end)
                    for token in entity:
                        token._.set(self.is_attribute, True)
        return doc

    def get_attribute(self, span):
        """Boolean getter for Doc and Span attribute

        Returns True if one of the tokens in the span or doc
        is of the defined attribute of this pipeline component, to be called in the main pipeline
        and add the 'has_attribute' if any of the token matches the custom attribute

        Args:
            span (Span): sequence of tokens to get attribute from

        Returns:
            True if any of the tokens has designated attribute
        """
        return any([token._.get(self.is_attribute) for token in span])
