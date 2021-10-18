"""
Everything related to file in- and output.
"""

from abc import ABC, abstractclassmethod, abstractstaticmethod
import io
import json
from pathlib import Path
import sys
from typing import Any, Dict, Optional


class StdInNotSupported(Exception):
    """
    Exception raised when user tries to load data into the application using
    the standard input (stdin) for a `File` implementation which doesn't
    support this. Also see `File.__supports_std` for more information on that
    matter.
    """

    def __init__(self, file: "File"):
        super().__init__(
            f"{file.format_name()} does not support the input of data using "
            "stdin. Please specify a input path."
        )


class StdOutNotSupported(Exception):
    """
    Exception raised when user tries to load data into the application using
    the standard output (stdout) for a `File` implementation which doesn't
    support this. Also see `File.__supports_std` for more information on that
    matter.
    """

    def __init__(self, file: "File"):
        super().__init__(
            f"{file.format_name()} does not support the input of data using "
            "stdout. Please specify a output path."
        )


class File(ABC):
    """
    Provides the in- and output of data into and out of nocopy-cli.

    A file can also be a stdin or out. This is choosen if no input or output
    file was given by the user. The children classes of `File` implement the
    functionality for a certain data type (like JSON).
    """

    input_path: Optional[Path]
    """Optional path to input file."""
    output_path: Optional[Path]
    """Optional path to input file."""

    def __init__(
        self,
        input_path: Optional[Path],
        output_path: Optional[Path],
    ):
        self.input_path = input_path
        self.output_path = output_path

    def load(self) -> Dict[str, Any]:
        """Load the data in the file and returns the data as a dict."""
        if self.input_path is None:
            if not self.supports_std():
                raise StdInNotSupported(self)
            return self.parse(io.BytesIO(self.__read_stdin()))

        with open(self.input_path, "rb") as file:
            return self.parse(file)

    def save(self, data: Dict[str, Any]):
        """Saves/outputs the data to the file/stdout."""
        if self.output_path is None:
            if not self.supports_std():
                raise StdOutNotSupported(self)
            print(self.dump(data).decode("utf-8"))
        else:
            with open(self.output_path, "wb") as file:
                file.write(self.dump(data))

    @staticmethod
    def __read_stdin() -> str:
        rsl = ""
        try:
            for line in sys.stdin:
                rsl += line
        except KeyboardInterrupt:
            sys.stdout.flush()
        return rsl

    @abstractclassmethod
    def format_name(cls) -> str:
        """
        Returns the name of the format supported by the given implementation of
        `File`. This is value is also used by the user interface to name this
        format.
        """
        pass

    @abstractclassmethod
    def supports_std(self) -> bool:
        """
        States whether the data type can be in-/outputted to/from the
        application via stdin and stdout. Motivation: Some file formats do not
        really make sense to be piped between multiple application in a shell
        like Excel's xlsx format.
        """
        pass

    @abstractstaticmethod
    def parse(raw: bytes) -> Dict[str, Any]:
        """
        Parses a given file (opened in binary mode) and returns it's structure
        as a dictionary.
        """
        pass

    @abstractstaticmethod
    def dump(data: Dict[str, Any]) -> bytes:
        """
        Return a bytes literal of the dumped data structured.
        """
        pass


class Json(File):
    """JSON implementation for `File`."""

    def __init__(self, *args):
        super().__init__(*args)

    @classmethod
    def format_name(cls) -> str:
        return "json"

    @classmethod
    def supports_std(self) -> bool:
        return True

    @staticmethod
    def parse(raw: bytes) -> Dict[str, Any]:
        return json.load(raw)

    @staticmethod
    def dump(data: Dict[str, Any]) -> bytes:
        return json.dumps(data).encode("utf-8")


def file(
    format_option: str,
    input_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> File:
    """
    Factory method for `File`.

    Returns the appropriate `File` implementation based on the given
    format_option.
    """
    if format_option == Json.format_name():
        return Json(input_path, output_path)
    raise ValueError(f"{format_option} is not supported by this application")
