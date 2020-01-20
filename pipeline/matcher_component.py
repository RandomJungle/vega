# coding: utf8

from spacy.language import Language
from spacy.matcher.matcher import Matcher
from spacy.tokens import Doc, Span, Token


class MatcherComponent(object):
    """
    Matcher-based pipeline component

    Note:
        optional merging of matched spans, provided in utils class
        are function that allow to control match type (all, overlapping, etc.)
    """

    def __init__(self,
                 nlp: Language,
                 matcher: Matcher,
                 component_name: str,
                 attribute_name: str,
                 merge_on_match: bool = True):
        """
        Constructor of MatcherComponent object

        Args:
            nlp (Doc): Spacy Doc object
            component_name (str): Unique name of this component
            attribute_name (str): label to add for custom attribute
            merge_on_match (bool): optional merging on match option, default to True
            validate (bool): optional pattern validation, default to False
        """
        self.nlp = nlp
        self.matcher = matcher
        self.name = component_name
        self.is_attribute = f"is_{attribute_name}"
        self.has_attribute = f"has_{attribute_name}"
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

        Args:
            doc: document object

        Returns:
            doc object modified
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
