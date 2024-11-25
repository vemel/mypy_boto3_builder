"""
Base stubs/docs generator.

Copyright 2024 Vlad Emelianov
"""

import shutil
import tempfile
from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path
from typing import ClassVar

from mypy_boto3_builder.cli_parser import CLINamespace
from mypy_boto3_builder.enums.product_type import ProductType
from mypy_boto3_builder.exceptions import AlreadyPublishedError
from mypy_boto3_builder.logger import get_logger
from mypy_boto3_builder.package_data import BasePackageData
from mypy_boto3_builder.parsers.service_package_parser import ServicePackageParser
from mypy_boto3_builder.postprocessors.base import BasePostprocessor
from mypy_boto3_builder.service_name import ServiceName
from mypy_boto3_builder.structures.package import Package
from mypy_boto3_builder.structures.service_package import ServicePackage
from mypy_boto3_builder.utils.github import download_and_extract
from mypy_boto3_builder.utils.package_builder import PackageBuilder
from mypy_boto3_builder.utils.pypi_manager import PyPIManager
from mypy_boto3_builder.writers.package_writer import PackageWriter


class BaseGenerator(ABC):
    """
    Base stubs/docs generator.

    Arguments:
        service_names -- Selected service names
        master_service_names -- Service names included in master
        config -- CLI configuration
        version -- Package build version
        cleanup -- Whether to cleanup generated files
    """

    service_package_data: ClassVar[type[BasePackageData]]
    service_template_path: ClassVar[Path]

    def __init__(
        self,
        service_names: Sequence[ServiceName],
        master_service_names: Sequence[ServiceName],
        config: CLINamespace,
        version: str,
        *,
        cleanup: bool,
    ) -> None:
        self.__temp_path: Path | None = None
        self._cleanup_dirs: list[Path] = []
        self._downloaded_static_files_path: Path | None = None

        self.service_names = service_names
        self.master_service_names = master_service_names
        self.config = config
        self.logger = get_logger()
        self.version = version or self.get_library_version()
        self.cleanup = cleanup
        self.package_writer = PackageWriter(
            output_path=self.output_path,
            generate_package=self.is_package(),
            cleanup=cleanup,
        )

    def is_package(self) -> bool:
        """
        Whether to generate ready-to-install package or installed package.
        """
        return not any(output_type.is_installed() for output_type in self.config.output_types)

    def is_packaged(self) -> bool:
        """
        Whether to build wheel or sdist.
        """
        return any(output_type.is_packaged() for output_type in self.config.output_types)

    def is_package_temporary(self) -> bool:
        """
        Whether to preserve generated package.
        """
        return not any(output_type.is_preserved() for output_type in self.config.output_types)

    @property
    def _temp_path(self) -> Path:
        if not self.__temp_path:
            self.__temp_path = Path(tempfile.TemporaryDirectory(delete=False).name)
            self._cleanup_dirs.append(self.__temp_path)
        return self.__temp_path

    @property
    def output_path(self) -> Path:
        """
        Output path.
        """
        if self.is_package_temporary():
            return self._temp_path
        return self.config.output_path

    def _get_or_download_static_files_path(
        self,
        static_path: Path,
        download_url: str | None = None,
    ) -> Path:
        """
        Get path to static files. Download if needed.
        """
        if not self.config.download_static_stubs or not download_url:
            return static_path

        if self._downloaded_static_files_path:
            return self._downloaded_static_files_path

        self.logger.debug(f"Downloading static files from {download_url}")
        temp_dir_path = Path(tempfile.TemporaryDirectory(delete=False).name)
        self._cleanup_dirs.append(temp_dir_path)
        self._downloaded_static_files_path = download_and_extract(download_url, temp_dir_path)

        self.logger.debug(f"Downloaded static files to {self._downloaded_static_files_path}")

        return self._downloaded_static_files_path

    @abstractmethod
    def get_postprocessor(self, service_package: ServicePackage) -> BasePostprocessor:
        """
        Get postprocessor for service package.
        """

    def get_library_version(self) -> str:
        """
        Get underlying library version.
        """
        return self.service_package_data.get_library_version()

    def _get_package_version(self, pypi_name: str, version: str) -> str:
        if self.config.disable_smart_version:
            return version
        pypi_manager = PyPIManager(pypi_name)
        if not pypi_manager.has_version(version):
            return version

        if self.config.skip_published:
            raise AlreadyPublishedError(f"{pypi_name} {version} is already on PyPI")

        return pypi_manager.get_next_version(version)

    @abstractmethod
    def generate_stubs(self) -> Sequence[Package]:
        """
        Generate main stubs.
        """
        raise NotImplementedError("Method should be implemented in child class")

    @abstractmethod
    def generate_full_stubs(self) -> Sequence[Package]:
        """
        Generate full stubs.
        """
        raise NotImplementedError("Method should be implemented in child class")

    @abstractmethod
    def generate_custom_stubs(self) -> Sequence[Package]:
        """
        Generate custom stubs.
        """
        raise NotImplementedError("Method should be implemented in child class")

    def _generate_full_stubs_services(self, package: Package) -> None:
        package_writer = PackageWriter(
            output_path=self.output_path / package.directory_name,
            generate_package=False,
            cleanup=False,
        )
        total_str = f"{len(self.service_names)}"
        for index, service_name in enumerate(self.service_names):
            current_str = f"{{:0{len(total_str)}}}".format(index + 1)
            progress_str = f"[{current_str}/{total_str}]"

            self.logger.info(
                f"{progress_str} Generating {service_name.boto3_name} package directory",
            )
            service_package = self._parse_service_package(
                service_name=service_name,
                version=package.version,
                package_data=package.data,
            )
            ServicePackageParser.mark_safe_typed_dicts(service_package)

            service_package.pypi_name = package.pypi_name
            package_writer.write_service_package(
                package=service_package,
                templates_path=self.service_template_path,
            )

    @abstractmethod
    def generate_docs(self) -> None:
        """
        Generate service and master docs.
        """

    def generate_product(self, product_type: ProductType) -> None:
        """
        Run generator for a product type.
        """
        packages: list[Package] = []
        match product_type:
            case ProductType.stubs:
                packages.extend(self.generate_stubs())
            case ProductType.service_stubs:
                packages.extend(self.generate_service_stubs())
            case ProductType.docs:
                self.generate_docs()
            case ProductType.full:
                packages.extend(self.generate_full_stubs())
            case ProductType.custom:
                packages.extend(self.generate_custom_stubs())

        if self.is_packaged():
            package_builder = PackageBuilder(
                build_path=self.output_path,
                output_path=self.config.output_path,
            )
            for package in packages:
                package_builder.build(package, self.config.output_types)

    def _parse_service_package(
        self,
        service_name: ServiceName,
        version: str,
        package_data: type[BasePackageData],
    ) -> ServicePackage:
        self.logger.debug(f"Parsing {service_name.boto3_name}")
        parser = ServicePackageParser(service_name, package_data, version)
        service_package = parser.parse()

        postprocessor = self.get_postprocessor(service_package)
        postprocessor.generate_docstrings()
        postprocessor.process_package()

        postprocessor.extend_literals()
        postprocessor.replace_self_ref_typed_dicts()
        return service_package

    def _process_service(
        self,
        service_name: ServiceName,
        version: str,
        package_data: type[BasePackageData],
        templates_path: Path,
    ) -> ServicePackage:
        service_package = self._parse_service_package(
            service_name=service_name,
            version=version,
            package_data=package_data,
        )
        ServicePackageParser.mark_safe_typed_dicts(service_package)

        self.logger.debug(f"Writing {service_name.boto3_name}")
        self.package_writer.write_service_package(
            service_package,
            templates_path=templates_path,
        )
        return service_package

    def _process_service_docs(
        self,
        service_name: ServiceName,
        version: str,
        package_data: type[BasePackageData],
        templates_path: Path,
    ) -> ServicePackage:
        service_package = self._parse_service_package(
            service_name=service_name,
            version=version,
            package_data=package_data,
        )

        self.logger.debug(f"Writing {service_name.boto3_name}")
        self.package_writer.write_service_docs(
            service_package,
            templates_path=templates_path,
        )
        return service_package

    def generate_service_stubs(self) -> list[ServicePackage]:
        """
        Generate service stubs.
        """
        total_str = f"{len(self.service_names)}"
        packages: list[ServicePackage] = []
        for index, service_name in enumerate(self.service_names):
            current_str = f"{{:0{len(total_str)}}}".format(index + 1)
            progress_str = f"[{current_str}/{total_str}]"

            pypi_name = self.service_package_data.get_service_pypi_name(service_name)
            try:
                version = self._get_package_version(pypi_name, self.version)
            except AlreadyPublishedError:
                self.logger.info(f"Skipping {pypi_name} {self.version}, already on PyPI")
                continue

            self.logger.info(f"{progress_str} Generating {pypi_name} {version}")
            package = self._process_service(
                service_name=service_name,
                version=version,
                package_data=self.service_package_data,
                templates_path=self.service_template_path,
            )
            packages.append(package)

        return packages

    def cleanup_temporary_files(self) -> None:
        """
        Cleanup temporary files.
        """
        for dir_path in self._cleanup_dirs:
            if not dir_path.exists():
                continue

            self.logger.debug(f"Removing {dir_path}")
            shutil.rmtree(dir_path)
