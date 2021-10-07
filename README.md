# nocopy-cli

Simple CLI client application for the Airtable alternative [NocoDB](https://nocodb.com/) using the [nocopy library](https://github.com/72nd/nocopy). The main aim is to simplify the in- and export of data to and from your NocoDB instance and bulk updating/altering of entries. Features:

- Download the content of a NocoDB table into a file or pipe them into a another application via stdout. Supports [NocoDB's query features](https://docs.nocodb.com/developer-resources/rest-apis#query-params).
- Upload data from your client and create new entries in your NocoDB table.
- Supported data formats/structures: [YAML](https://en.wikipedia.org/wiki/YAML), [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) and [JSON](https://en.wikipedia.org/wiki/JSON).
- Update existing entries in your NocoDB using a JSON, YAML or CSV file.
- Update a specific field for entries which meet certain conditions.
- And more...


## Installation

As you would expect:

```shell script
pip3 install nocopy-cli
```

To ensure everything went well try:

```shell script
nocopy
```


## Configuration

The application has to know the URL and the secret token of your API endpoint. There are three different possibilities to define them:

1. Using the `-u/--url` and `-k/--token` flags.
2. Setting the `NOCO_URL` and `NOCO_TOKEN` environment variable.
3. Using a configuration file.

The configuration file is a simple JSON file. Which can be generated using the CLI:

```shell script
nocopy init -o config.json
```


## A word on in/output files and their formats

A number of nocopy-cli's operation consist of reading or writing from/to a file. Currently [YAML](https://en.wikipedia.org/wiki/YAML), [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) and [JSON](https://en.wikipedia.org/wiki/JSON) are supported ether as file (defined using the `-i/--input` respective `-o/--output` flags) as well as piping the data per stdin/stdout. The application tries to determine the format based on the file extension. Otherwise YAML will be used. Use the `-f/--format` flag to specify the format.


## Usage

For the examples we assume our database contains the table `persons` with the following schema:

```
id			integer		<- Given by NocoDB
nullable 	false		<- "
readOnly 	true		<- "
name		string
created_at	string
updated_at	string
email		string
gender		string
age			integer
cars		integer		<- Foreign key to 'cars' table
color		string
```


### Aggregate

Aggregate records using functions. _To be documented. Please use `nocopy aggregate --help` for more information on that command._


### Count

Counts the entries in a table. This command is especially useful when used in combination with the `--where` flag using [NocoDB's query syntax](https://docs.nocodb.com/developer-resources/rest-apis/#comparison-operators). Examples:


```shell script
# How many persons are in the table?
nocopy count -c config.json -t persons
> 200

# How many persons favorite color is blue?
nocopy count -c config.json -t persons --where "(color,eq,Blue)"
> 23
```


### Find first

Find the first record matching the given query. _To be documented. Please use `nocopy find-first --help` for more information on that command._


### Group by

Group records by given column. _To be documented. Please use `nocopy find-first --help` for more information on that command._


### Init

Just a convince function. Generates a new and empty config file.

```shell script
nocopy init -o config.json
```

### Pull

Pull/download the records from the NocoDB. Currently [YAML](https://en.wikipedia.org/wiki/YAML) (default), [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) and [JSON](https://en.wikipedia.org/wiki/JSON) are supported as a output format. If no output file is specified (using `-o/--output`) the output will be written to the stdout. The format is determined using the file extension alternatively use the `-f/--format` option.

The [NocoDB's query parameters](https://docs.nocodb.com/developer-resources/rest-apis#query-params) are supported:

- `--where` Complicated where conditions.
- `--limit` Number of rows to get(SQL limit value).
- `--offset` Offset for pagination(SQL offset value).
- `--sort` Sort by column name, Use `-` as prefix for descending sort.
- `--fields` Required column names in result.
- `--fields1` Required column names in child result.

If you you need a more »quick and dirty« approach on search you can use the `-q/--query` option. If specified a fuzzy search is performed on all values received from NocoDB.

Examples:

```shell script
# Download all record in the table 'persons' to a csv file.
nocopy -c config.json -t persons -o persons.csv

# Output all persons in the age of 23 in the JSON format to stdout.
nocopy -c config.json -t persons --format json --where "(age,eq,23)"
> ...
```


### Purge

Deletes all records of a table as there is no native function for that in NocoDB (yet).

```shell script
nocopy purge -c config.json -t guests
```


### Push

Add new entries to a table in NocoDB. The application takes YAML, JSON or CSV files as a input. When using CSV as a input the first row has to contain the names of the respective fields in your NocoDB model. Using the `template` command (see below) you can generate an empty file which contains the correct column names.

```shell script
nocopy push -c config.json -t guests -i new-persons.csv
```

Empty cells are parsed as `None`.


### Sum

Calculate the sum of a field for all matching records. _To be documented. Please use `nocopy sum --help` for more information on that command._


### Template

Generates an file with the correct header row/keys. The table on the NocoDB server has to contain at least one record for this to work.)

```shell script
# Write an empty CSV file with the header row to the disk.
nocopy template -c config.json -t persons -o lessons-template.csv

# Get the structure for YAML.
nocopy template -c config.json -t persons
> - age: null
>   car: null
>   color: null
>   created_at: null
>   email: null
>   gender: null
>   id: null
>   name: null
>   something: null
>   updated_at: null
```


### Update

Updates one or more existing record in your NocoDB table. The input has to provide the `id` of the record in NocoDB. This command is especially useful when used in combination with `pull`. Take this input files as example:

`to-update.json`:

```json
{
	"id": 192,
	"age": 42,
}
```

`to-update.csv`:

```csv
id,age
109,23
```


```shell script
# Change the age of the person with the id '192' to 42.
nocopy update -c config.json -t persons -i to-update.json

# Change the age of the person with the id '109' to 23.
nocopy update -c config.json -t persons -i to-update.csv
```


### Update field

Changes the fields of matching records to a given value.

```shell script
# Set the favorite color of all persons with the age of 23 to red.
nocopy update-field -c config.json -t persons --where "(age,eq,23)" --field color --value red
```
