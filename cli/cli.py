"""
Nocopy CLI application.
"""

import csv
import io
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

import click
from pydantic import BaseModel
from thefuzz import process as fuzz_process
import yaml

from nocopy import Client
from nocopy.client import build_url
from nocopy import cli_options


class Config(BaseModel):
    """Config file."""

    base_url: str
    """Base URL of the NocoDB API."""
    auth_token: str
    """JWT authentication token."""

    @classmethod
    def from_file(cls, path: Path):
        """Reads the `Config` as a JSON to a file."""
        with open(path, "r") as f:
            return cls.parse_raw(f.read())

    def to_file(self, path: Path):
        """writes the `Config` as a JSON to a file."""
        with open(path, "w") as f:
            f.write(self.json())


def __check_get_config(
    config_file: Optional[Path],
    url: Optional[str],
    token: Optional[str],
) -> Config:
    got_config = config_file is not None
    got_url = url is not None or url == ""
    got_token = token is not None or token == ""

    if got_config and (got_url or got_token):
        raise click.BadOptionUsage(
            "use ether a config file _or_ the parameters for --url and --token"
        )
    if got_url ^ got_token:
        raise click.BadOptionUsage(
            "if defined by parameter _both_ --url and --token have to be set"
        )
    if got_url and got_token:
        return Config(url, token)
    if not got_config:
        raise click.BadOptionUsage(
            "connection information missing, use a config file or the "
            "parameters for --url and --token"
        )
    return Config.from_file(config_file)


def __determine_file_type(
    file: Optional[Path],
    format_option: Optional[str]
) -> str:
    if format_option is not None:
        return format_option
    if file is not None:
        if file.suffix.lower() == ".json":
            return "JSON"
        elif file.suffix.lower() == ".csv":
            return "CSV"
        elif file.suffix.lower() == ".yaml" or file.suffix.lower() == ".yml":
            return "YAML"
        else:
            print(f"{file.suffix} is a unknown file type, default to YAML")
    return "YAML"


def __load_csv(input_file: Path) -> Dict[str, Any]:
    with open(input_file) as f:
        data = csv.DictReader(f)
        rsl = []
        for entry in data:
            for field in entry:
                if entry[field] == "":
                    entry[field] = None
            rsl.append(entry)
    return rsl


def __load_input(
    input_file: Optional[Path],
    format_option: Optional[str],
) -> Dict[str, Any]:
    format_option = __determine_file_type(input_file, format_option)
    if format_option == "YAML":
        return yaml.load(open(input_file))
    elif format_option == "JSON":
        return json.load(open(input_file))
    elif format_option == "CSV":
        return __load_csv(input_file)


def __get_client(
    config_file: Path,
    url: str,
    table: str,
    token: str,
) -> Client:
    config = __check_get_config(config_file, url, token)
    return Client(
        build_url(config.base_url, table),
        config.auth_token,
    )


def __get_csv(data: Dict[str, Any], only_header: bool = False) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=data[0].keys(),
        quotechar='"',
    )
    writer.writeheader()
    if not only_header:
        for entry in data:
            writer.writerow(entry)
    return buffer.getvalue()


def __write_output(
    output_file: Optional[Path],
    format_option: Optional[str],
    data: List[Dict[str, Any]],
    only_header: bool = False,
):
    format_option = __determine_file_type(output_file, format_option)
    if format_option == "YAML":
        rsl = yaml.dump(data)
    elif format_option == "JSON":
        rsl = json.dumps(data)
    elif format_option == "CSV":
        rsl = __get_csv(data, only_header=only_header)

    if output_file is not None:
        with open(output_file, "w") as f:
            f.write(rsl)
    else:
        print(rsl)


@click.group()
def cli():
    """CLI tools for NocoDB."""


@click.command()
@cli_options.config
@cli_options.where
@cli_options.table
def count(
    config_file: Path,
    where: Optional[str],
    url: str,
    table: str,
    token: str,
):
    """Count the records in a table."""
    client = __get_client(config_file, url, table, token)
    print(client.count(where=where))


@click.command()
@cli_options.config
@cli_options.format
@cli_options.output
@cli_options.column_name
@cli_options.where
@cli_options.limit
@cli_options.offset
@cli_options.sort
@cli_options.table
def group_by(
    config_file: Path,
    file_format: Optional[str],
    output_file: Path,
    column_name: Optional[str],
    where: Optional[str],
    limit: Optional[int],
    offset: Optional[int],
    sort: Optional[str],
    url: str,
    table: str,
    token: str,
):
    """Group records by given column."""
    client = __get_client(config_file, url, table, token)
    data = client.group_by(
        column_name=column_name,
        where=where,
        limit=limit,
        offset=offset,
        sort=sort,
    )
    __write_output(output_file, file_format, data)


@click.command()
@cli_options.config
@cli_options.format
@cli_options.output
@cli_options.column_name
@cli_options.func
@cli_options.havign
@cli_options.fields
@cli_options.limit
@cli_options.offset
@cli_options.sort
@cli_options.table
def aggregate(
    config_file: Path,
    file_format: Optional[str],
    output_file: Path,
    column_name: Optional[str],
    func: Optional[str],
    having: Optional[str],
    fields: Optional[str],
    limit: Optional[int],
    offset: Optional[int],
    sort: Optional[str],
    url: str,
    table: str,
    token: str,
):
    """Aggregate records using functions."""
    client = __get_client(config_file, url, table, token)
    data = client.aggregate(
        column_name=column_name,
        func=func,
        having=having,
        fields=fields,
        limit=limit,
        offset=offset,
        sort=sort,
    )
    __write_output(output_file, file_format, data)


@click.command()
@cli_options.config
@cli_options.format
@cli_options.output
@cli_options.where
@cli_options.offset
@cli_options.sort
@cli_options.fields
@cli_options.table
def find_first(
    config_file: Path,
    file_format: Optional[str],
    output_file: Path,
    where: Optional[str],
    offset: Optional[int],
    sort: Optional[str],
    fields: Optional[str],
    url: str,
    table: str,
    token: str,
):
    """Find the first record matching the given query."""
    client = __get_client(config_file, url, table, token)
    data = client.find_first(
        where=where,
        offset=offset,
        sort=sort,
        fields=fields,
    )
    __write_output(output_file, file_format, data)


@click.command()
@cli_options.config
@cli_options.format
@cli_options.input
@cli_options.table
def push(
    config_file: Path,
    file_format: Optional[str],
    input_file: Path,
    url: str,
    table: str,
    token: str,
):
    """Upload the content of a JSON/CSV file to NocoDB."""
    client = __get_client(config_file, url, table, token)
    data = __load_input(input_file, file_format)

    client.add(data)


@click.command()
@cli_options.output
def init(output_file: Path):
    """Generate an empty configuration file."""
    cfg = Config(
        base_url="https:///noco.example.com/nc/project/api/v1/",
        auth_token="A-SECRET-TOKEN-FNORD",
    )
    cfg.to_file(output_file)


@click.command()
@cli_options.config
@cli_options.format
@cli_options.fuzzy_query
@cli_options.output
@cli_options.where
@cli_options.limit
@cli_options.offset
@cli_options.sort
@cli_options.fields
@cli_options.fields1
@cli_options.table
def pull(
    config_file: Path,
    file_format: Optional[str],
    output_file: Path,
    where: Optional[str],
    limit: Optional[int],
    offset: Optional[int],
    sort: Optional[str],
    fields: Optional[str],
    fields1: Optional[str],
    fuzzy_query: Optional[str],
    url: str,
    table: str,
    token: str,
):
    """Pull the records from a NocoDB instance."""
    client = __get_client(config_file, url, table, token)
    data = client.list(
        where=where,
        limit=limit,
        offset=offset,
        sort=sort,
        fields=fields,
        fields1=fields1,
        as_dict=True,
    )
    if fuzzy_query is not None:
        fuzz = fuzz_process.extractBests(fuzzy_query, data, score_cutoff=50)
        data = []
        for rsl in fuzz:
            data.append(rsl[0])
    __write_output(output_file, file_format, data)


@click.command()
@cli_options.config
@cli_options.table
def purge(
    config_file: Path,
    url: str,
    table: str,
    token: str,
):
    """Delete the all content of a table."""
    client = __get_client(config_file, url, table, token)

    print(
        f"This will PERMANENTLY delete ALL data in table {table} on {client.base_url}")
    user = input("Is this ok (Y/n): ")
    if user != "Y":
        print("aborting...")
        sys.exit(0)
    # Being extra annoying because the user is me...
    user = input(
        "Sure? Think again and then type the name of the table to proceed: "
    )
    if user != table:
        sys.exit(0)
    records = client.list()
    with click.progressbar(
        records,
        label="Purge records...",
        show_pos=True,
    ) as bar:
        for record in bar:
            client.delete(record["id"])


@click.command("sum")
@cli_options.config
@cli_options.format
@cli_options.output
@cli_options.where
@cli_options.limit
@cli_options.offset
@cli_options.sort
@cli_options.field
@cli_options.table
def sum_command(
    config_file: Path,
    file_format: Optional[str],
    output_file: Path,
    where: Optional[str],
    limit: Optional[int],
    offset: Optional[int],
    sort: Optional[str],
    field: str,
    url: str,
    table: str,
    token: str,
):
    """Sum of the values of a requested field"""
    client = __get_client(config_file, url, table, token)
    data = client.list(
        where=where,
        limit=limit,
        offset=offset,
        sort=sort,
        as_dict=True,
    )
    rsl = 0
    for record in data:
        value = record[field]
        if value is not None:
            rsl += value
    print(rsl)


@click.command()
@cli_options.config
@cli_options.format
@cli_options.output
@cli_options.table
def template(
    config_file: Path,
    file_format: Optional[str],
    output_file: Optional[Path],
    url: str,
    table: str,
    token: str,
):
    """Generate a empty template for a specified table."""
    client = __get_client(config_file, url, table, token)
    data = client.list()[0]
    for key in data:
        data[key] = None
    __write_output(output_file, file_format, [data], only_header=True)


@click.command()
@cli_options.config
@cli_options.input
@cli_options.table
def update(
    config_file: Path,
    input_file: Path,
    url: str,
    table: str,
    token: str,
):
    """Update records."""
    client = __get_client(config_file, url, table, token)
    data = __load_csv(input_file)
    client.bulk_update(data)


@click.command()
@cli_options.config
@cli_options.field
@cli_options.where
@cli_options.value
@cli_options.table
def update_field(
    config_file: Path,
    field: str,
    where: Optional[str],
    value: str,
    url: str,
    table: str,
    token: str,
):
    """Set field value of matching records"""
    client = __get_client(config_file, url, table, token)
    records = client.list(where=where, as_dict=True)

    print(
        f"About to change the field {field} to '{value}' in {len(records)} occurrences"
    )
    user = input("Is this ok (Y/n): ")
    if user != "Y":
        print("aborting...")
        sys.exit(0)
    with click.progressbar(
        records,
        label=f"update field {field}",
        show_pos=True,
    ) as bar:
        for record in bar:
            client.update(record["id"], {field: value})


cli.add_command(aggregate)
cli.add_command(count)
cli.add_command(group_by)
cli.add_command(find_first)
cli.add_command(init)
cli.add_command(push)
cli.add_command(pull)
cli.add_command(purge)
cli.add_command(sum_command)
cli.add_command(template)
cli.add_command(update)
cli.add_command(update_field)


if __name__ == "__main__":
    cli()
