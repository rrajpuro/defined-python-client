# Command-line guide

`definedcli` exposes the Defined Networking resources as a hierarchy of
commands. Successful commands write one JSON document or table to stdout;
diagnostics are written to stderr.

## Install and verify

```bash
uv tool install git+https://github.com/rrajpuro/defined-python-client
definedcli --version
definedcli --help
```

For a local checkout:

```bash
uv tool install .
```

Use `uv tool install --force .` to refresh an existing local installation.

## Authenticate

Export an API key created in the
[Defined Networking admin panel](https://admin.defined.net/settings/api-keys):

```bash
export DEFINED_API_KEY='dnkey-...'
definedcli hosts list
```

The CLI does not accept credentials as command-line arguments and does not
store profiles. `definedcli downloads list` uses the public downloads endpoint
and does not require a key.

## Global syntax

```text
definedcli [GLOBAL OPTIONS] RESOURCE COMMAND [COMMAND OPTIONS]
```

Global options must precede the resource:

| Option | Purpose |
| --- | --- |
| `--base-url URL` | Override the API server |
| `--timeout SECONDS` | Set the request timeout; defaults to 30 seconds |
| `--output json\|table` | Select output format; defaults to JSON |
| `--version` | Print the installed version |

`--base-url` takes precedence over `DEFINED_BASE_URL`, which takes precedence
over `https://api.defined.net`.

Use nested help to discover required options and accepted values:

```bash
definedcli hosts --help
definedcli hosts create --help
definedcli routes update --help
```

## Command reference

| Resource | Commands |
| --- | --- |
| `hosts` | `create`, `create-with-enrollment`, `list`, `get`, `get-by-name`, `find-by-name`, `update`, `replace`, `delete`, `block`, `unblock`, `debug-command`, `create-enrollment-code`, `update-tags`, `add-tag`, `remove-tag` |
| `roles` | `create`, `list`, `get`, `update`, `replace`, `delete` |
| `routes` | `create`, `list`, `get`, `get-by-name`, `find-by-name`, `update`, `replace`, `delete`, `update-router-host` |
| `tags` | `create`, `list`, `get`, `find-by-key`, `update`, `replace`, `delete`, `subscribe-route`, `unsubscribe-route` |
| `networks` | `create`, `list`, `get`, `update`, `replace` |
| `audit-logs` | `list` |
| `downloads` | `list` |

## Common workflows

List resources as a table:

```bash
definedcli --output table hosts list
definedcli --output table networks list
```

Create a host with repeatable collection options:

```bash
definedcli hosts create \
  --name edge-router-01 \
  --network-id network-XXXXX \
  --role-id role-XXXXX \
  --static-address '203.0.113.10:4242' \
  --tag 'env:prod' \
  --tag 'region:us-central'
```

Find by an exact name when an ID is not known:

```bash
definedcli hosts get-by-name --name edge-router-01
definedcli routes find-by-name --name office
```

`get-by-name` fails when no match exists. `find-by-name` succeeds and returns a
`null` data value.

Perform focused, safe changes:

```bash
definedcli hosts update --host-id host-XXXXX --name edge-router-02
definedcli hosts add-tag --host-id host-XXXXX --tag env:prod
definedcli routes update-router-host \
  --route-id route-XXXXX \
  --host-id host-YYYYY
definedcli networks update \
  --network-id network-XXXXX \
  --no-lighthouses-as-relays
```

Deletes are non-interactive. Check the resource ID before invoking a `delete`
command.

## Structured JSON values

Options for nested API values accept either inline JSON or a `file://` path to
a UTF-8 JSON file. The CLI validates the top-level JSON type locally.

Inline array:

```bash
definedcli roles create \
  --name web \
  --firewall-rules \
  '[{"protocol":"TCP","allowedRoleID":"role-XXXXX","portRange":{"from":443,"to":443}}]'
```

Object loaded from a file:

```bash
definedcli routes create \
  --name office \
  --router-host-id host-XXXXX \
  --routable-cidrs file://route-cidrs.json
```

Debug command arguments are also JSON:

```bash
definedcli hosts debug-command \
  --host-id host-XXXXX \
  --command StreamLogs \
  --command-args '{"durationSeconds":60,"level":"info"}'
```

YAML, AWS shorthand syntax, and a generic `--cli-input-json` option are not
supported.

## Update or replace

The API uses full-replacement `PUT` semantics. CLI `update` commands protect
omitted fields by fetching the current resource and merging only the options
provided. Explicit empty collections, empty strings, and false values are still
applied.

```bash
definedcli tags update \
  --tag env:prod \
  --clear-route-subscriptions
```

Use `replace` only when the complete API-shaped mutable document is already
available. It sends the decoded object unchanged and does not make a preliminary
GET request.

```bash
definedcli hosts replace \
  --host-id host-XXXXX \
  --document file://host-replacement.json
```

The safe update sequence is not atomic: another writer can change the resource
between the GET and PUT.

## Output and pagination

JSON is the default. It preserves the API envelope without adding an `ok` or
`result` wrapper:

```bash
definedcli hosts list > hosts.json
```

Table output renders the value under `data` for human inspection:

```bash
definedcli --output table hosts get --host-id host-XXXXX
```

List commands fetch all pages by default. The page size can be set from 1 to
500, a continuation token can select the starting point, and `--no-paginate`
requests only one page:

```bash
definedcli hosts list --page-size 250
definedcli hosts list --starting-token TOKEN
definedcli hosts list --no-paginate
```

Auto-pagination combines page items under `data`, preserves stable metadata,
and removes stale continuation cursors. If a later page fails, no partial JSON
document is written.

## Errors and exit status

| Status | Meaning |
| --- | --- |
| `0` | Command succeeded |
| `1` | API, server, or network request failed |
| `2` | Command usage or local configuration is invalid |

Errors go to stderr so scripts can safely redirect stdout. Configured API keys
and returned enrollment codes are redacted from diagnostics.
