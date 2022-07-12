"""
Wrapper for type annotations imported from 3rd party libraries, like `boto3.service.Service`.
"""
from mypy_boto3_builder.import_helpers.import_record import ImportRecord
from mypy_boto3_builder.import_helpers.import_string import ImportString
from mypy_boto3_builder.type_annotations.fake_annotation import FakeAnnotation


class ExternalImport(FakeAnnotation):
    """
    Wrapper for type annotations imported from 3rd party libraries, like `boto3.service.Service`.

    Arguments:
        source -- Module import string.
        name -- Import name.
        alias -- Import local name.
    """

    def __init__(
        self,
        source: ImportString,
        name: str = "",
        alias: str = "",
    ) -> None:
        self.source: ImportString = source
        self.name: str = name
        self.alias: str = alias

    @property
    def import_record(self) -> ImportRecord:
        """
        Get import record required for using type annotation.
        """
        return ImportRecord(source=self.source, name=self.name, alias=self.alias)

    def __hash__(self) -> int:
        return hash(self.import_record.render())

    def render(self, parent_name: str = "") -> str:
        """
        Get string with local name to use.

        Returns:
            Import record local name.
        """
        return self.import_record.get_local_name()

    def get_import_record(self) -> ImportRecord:
        """
        Get import record required for using type annotation.
        """
        return self.import_record

    def copy(self) -> "ExternalImport":
        """
        Create a copy of type annotation wrapper.
        """
        return ExternalImport(self.source, self.name, self.alias)
