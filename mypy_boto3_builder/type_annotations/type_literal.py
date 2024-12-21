"""
Wrapper for `typing/typing_extensions.Literal` type annotations like `Literal['a', 'b']`.

Copyright 2024 Vlad Emelianov
"""

from collections.abc import Iterable
from pathlib import Path
from typing import Self

from mypy_boto3_builder.enums.service_module_name import ServiceModuleName
from mypy_boto3_builder.exceptions import TypeAnnotationError
from mypy_boto3_builder.import_helpers.import_record import ImportRecord
from mypy_boto3_builder.import_helpers.internal_import_record import InternalImportRecord
from mypy_boto3_builder.type_annotations.fake_annotation import FakeAnnotation
from mypy_boto3_builder.type_annotations.type_annotation import TypeAnnotation
from mypy_boto3_builder.utils.jinja2 import render_jinja2_template


class TypeLiteral(FakeAnnotation):
    """
    Wrapper for `typing/typing_extensions.Literal` type annotations like `Literal['a', 'b']`.

    Arguments:
        name -- Literal name for non-inline.
        children -- Literal values.
        inline -- Render literal inline.
    """

    def __init__(self, name: str, children: Iterable[str]) -> None:
        self.children: set[str] = set(children)
        self.name: str = name
        if not children:
            raise TypeAnnotationError("Literal should have children")

    def get_sort_key(self) -> str:
        """
        Sort literals by name.
        """
        return self.name

    @property
    def inline(self) -> bool:
        """
        Whether Litereal should be rendered inline.

        1-value literals are rendered inline.
        """
        return len(self.children) == 1

    def render(self) -> str:
        """
        Render type annotation to a valid Python code for local usage.

        Returns:
            A string with a valid type annotation.
        """
        if self.inline:
            children = ", ".join([repr(i) for i in sorted(self.children)])
            return f"Literal[{children}]"

        return self.name

    def _get_import_records(self) -> set[ImportRecord]:
        """
        Get import record required for using type annotation.
        """
        if self.inline:
            return TypeAnnotation("Literal").get_import_records()

        return {InternalImportRecord(ServiceModuleName.literals, name=self.name)}

    def get_definition_import_records(self) -> set[ImportRecord]:
        """
        Get import record required for using Literal.
        """
        return TypeAnnotation("Literal").get_import_records()

    def __copy__(self) -> Self:
        """
        Create a copy of type annotation wrapper.
        """
        return self.__class__(self.name, self.children)

    def is_literal(self) -> bool:
        """
        Whether type annotation is `Literal`.
        """
        return True

    def add_child(self, child: FakeAnnotation) -> None:
        """
        Disabled method to avoid confusion.
        """
        raise TypeAnnotationError("Use add_literal_child function.")

    def is_same(self, other: Self) -> bool:
        """
        Check if literals have the same children.
        """
        return self.children == other.children

    def get_local_types(self) -> list[FakeAnnotation]:
        """
        Get internal types generated by builder.
        """
        return [self]

    def render_definition(self) -> str:
        """
        Render type annotation definition.
        """
        return render_jinja2_template(Path("common/literal.py.jinja2"), {"literal": self})
