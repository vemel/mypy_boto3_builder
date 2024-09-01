"""
Parent class for all type annotation wrappers.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Final, Self

from mypy_boto3_builder.import_helpers.import_record import ImportRecord
from mypy_boto3_builder.import_helpers.import_string import ImportString


class FakeAnnotation(ABC):
    """
    Parent class for all type annotation wrappers.
    """

    _sys_import_record: Final[ImportRecord] = ImportRecord(ImportString("sys"))

    def __hash__(self) -> int:
        """
        Calculate hash value based on string render.
        """
        return hash(self.render())

    def __eq__(self, other: object) -> bool:
        """
        Whether two annotations are equal.
        """
        if not isinstance(other, FakeAnnotation):
            return False

        return self.get_sort_key() == other.get_sort_key()

    def __lt__(self: Self, other: Self) -> bool:
        """
        Compare two annotations for sorting.
        """
        return self.get_sort_key() < other.get_sort_key()

    def __gt__(self: Self, other: Self) -> bool:
        """
        Compare two annotations for sorting.
        """
        return self.get_sort_key() > other.get_sort_key()

    def get_sort_key(self) -> str:
        """
        Get string to sort annotations.
        """
        return str(self)

    def __str__(self) -> str:
        """
        Render annotation usage as a valid Python statement.
        """
        return self.render()

    @abstractmethod
    def render(self) -> str:
        """
        Render type annotation to a valid Python code for local usage.
        """

    def _get_import_records(self) -> set[ImportRecord]:
        """
        Get import record required for using type annotation.
        """
        return set()

    def get_import_records(self) -> set[ImportRecord]:
        """
        Get all import records required for using type annotation.
        """
        result: set[ImportRecord] = set()
        import_records = self._get_import_records()
        for import_record in import_records:
            if not import_record.is_empty() and not import_record.source.is_builtins():
                result.add(import_record)

        return result

    def iterate_types(self) -> Iterator["FakeAnnotation"]:
        """
        Iterate over all used type annotations recursively including self.
        """
        yield self

    def is_dict(self) -> bool:
        """
        Whether type annotation is `Dict` or `TypedDict`.
        """
        return False

    def is_typed_dict(self) -> bool:
        """
        Whether type annotation is `TypedDict`.
        """
        return False

    def is_list(self) -> bool:
        """
        Whether type annotation is `List`.
        """
        return False

    def is_literal(self) -> bool:
        """
        Whether type annotation is `Literal`.
        """
        return False

    @abstractmethod
    def __copy__(self: Self) -> Self:
        """
        Create a copy of type annotation wrapper.
        """

    def copy(self: Self) -> Self:
        """
        Create a copy of type annotation wrapper.
        """
        return self.__copy__()

    def get_local_types(self) -> list["FakeAnnotation"]:
        """
        Get internal types generated by builder.
        """
        return []

    def render_definition(self) -> str:
        """
        Render type annotation for debug purposes.
        """
        return self.render()
