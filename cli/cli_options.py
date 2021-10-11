"""
Options for the click CLI.
"""

from pathlib import Path

import click


def config(func):
    func = click.option(
        "-c",
        "--config",
        "config_file",
        type=click.Path(
            exists=True,
            path_type=Path,
        ),
        required=False,
        help="path to config file",
    )(func)
    func = click.option(
        "-u",
        "--url",
        type=str,
        required=False,
        help="base URL of the NocoDB API",
        envvar="NOCO_URL",
    )(func)
    func = click.option(
        "-k",
        "--token",
        type=str,
        required=False,
        help="JWT authentication token",
        envvar="NOCO_TOKEN",
    )(func)
    return func


def format(func):
    func = click.option(
        "-f",
        "--format",
        "file_format",
        type=click.Choice(["CSV", "JSON", "YAML"], case_sensitive=False),
        help="specify in-/output format",
    )(func)
    return func


def fuzzy_query(func):
    func = click.option(
        "-q",
        "--query",
        "fuzzy_query",
        type=str,
        help="client side fuzzy query",
    )(func)
    return func


def input(func):
    func = click.option(
        "-i",
        "--input",
        "input_file",
        type=click.Path(
            exists=True,
            path_type=Path,
        ),
        required=True,
        help="path to input file",
    )(func)
    return func


def output(func):
    func = click.option(
        "-o",
        "--output",
        "output_file",
        type=click.Path(
            path_type=Path,
        ),
        help="path to output file",
    )(func)
    return func


def func(func):
    func = click.option(
        "--func",
        type=str,
        required=False,
        help="Agr. function(s), min, max, avg, sum, count",
    )(func)
    return func


def havign(func):
    func = click.option(
        "--having",
        type=str,
        required=False,
        help="having expression",
    )(func)
    return func


def column_name(func):
    func = click.option(
        "--column-name",
        type=str,
        required=False,
        help="column name",
    )(func)
    return func


def where(func):
    func = click.option(
        "-w",
        "--where",
        type=str,
        required=False,
        help="complicated where conditions",
    )(func)
    return func


def limit(func):
    func = click.option(
        "--limit",
        type=int,
        required=False,
        help="number of rows to get(SQL limit value)",
    )(func)
    return func


def offset(func):
    func = click.option(
        "--offset",
        type=int,
        required=False,
        help="offset for pagination(SQL offset value)",
    )(func)
    return func


def sort(func):
    func = click.option(
        "--sort",
        type=str,
        required=False,
        help="sort by column name, use `-` as prefix for desc. sort",
    )(func)
    return func


def field(func):
    func = click.option(
        "-f",
        "--field",
        type=str,
        required=True,
        help="which column should be changed",
    )(func)
    return func


def fields(func):
    func = click.option(
        "--fields",
        type=str,
        required=False,
        help="which columns to show in the result",
    )(func)
    return func


def fields1(func):
    func = click.option(
        "--fields1",
        type=str,
        required=False,
        help="required column names in child result",
    )(func)
    return func


def value(func):
    func = click.option(
        "-v",
        "--value",
        type=str,
        required=True,
        help="value to be set",
    )(func)
    return func


def table(func):
    func = click.option(
        "-t",
        "--table",
        type=str,
        required=True,
        help="select the table",
    )(func)
    return func
