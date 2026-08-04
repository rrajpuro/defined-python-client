# Python client guide

The package has two layers:

- Resource objects on `DefinedClient` map directly to API endpoints.
- Service classes compose resource calls for safe updates and convenient
  lookups.

Use resource objects when you need exact API behavior. Prefer services for
partial updates and common multi-request workflows.

## Install

Add the Git repository to a uv-managed project:

```bash
uv add git+https://github.com/rrajpuro/defined-python-client
```

The package requires Python 3.13 or newer.

For a standalone uv script, add a dependency block:

```python
# /// script
# requires-python = ">=3.13"
# dependencies = ["defined-client"]
#
# [tool.uv.sources]
# defined-client = { git = "https://github.com/rrajpuro/defined-python-client" }
# ///
```

Then run the script with `uv run --script your_script.py`.

## Create and close a client

Use a context manager so the underlying HTTP session is always closed:

```python
import os

from defined_client import DefinedClient

with DefinedClient(api_key=os.environ["DEFINED_API_KEY"]) as client:
    response = client.hosts.list(page_size=50)
    for host in response["data"]:
        print(host["id"], host["name"])
```

For a longer-lived client, close it explicitly:

```python
client = DefinedClient(api_key="dnkey-...")
try:
    response = client.networks.list()
finally:
    client.close()
```

`DefinedClient` accepts two optional configuration values:

```python
client = DefinedClient(
    api_key="dnkey-...",
    base_url="https://api.example.com",
    timeout=15,
)
```

An individual request can override the client timeout through the low-level
`client.get()`, `post()`, `put()`, and `delete()` methods.

## Resource objects

The client exposes these resource objects:

| Attribute | Operations |
| --- | --- |
| `client.hosts` | `create`, `create_with_enrollment`, `list`, `get`, `update`, `delete`, `block`, `unblock`, `debug_command`, `create_enrollment_code` |
| `client.roles` | `create`, `list`, `get`, `update`, `delete` |
| `client.routes` | `create`, `list`, `get`, `update`, `delete` |
| `client.tags` | `create`, `list`, `get`, `update`, `delete` |
| `client.networks` | `create`, `list`, `get`, `update` |
| `client.audit_logs` | `list` |
| `client.downloads` | `list` |

Every resource method returns the parsed API response dictionary. Resource data
is normally under `response["data"]`; list pagination information is under
`response["metadata"]`.

Create and retrieve a host:

```python
created = client.hosts.create(
    name="edge-router-01",
    network_id="network-XXXXX",
    role_id="role-XXXXX",
    tags=["env:prod"],
)

host_id = created["data"]["id"]
host = client.hosts.get(host_id)["data"]
```

Use the official
[Defined Networking API reference](https://docs.defined.net/api/defined-networking-api/)
for request fields, response fields, and required token scopes.

## Services and safe updates

The API update operations use full-replacement semantics. Low-level resource
`update()` calls should contain the complete mutable representation. Service
`safe_update()` methods instead perform a GET, merge supplied changes, and PUT
the result.

```python
from defined_client import (
    HostService,
    NetworkService,
    RoleService,
    RouteService,
    TagService,
)

hosts = HostService(client)
roles = RoleService(client)
routes = RouteService(client)
tags = TagService(client)
networks = NetworkService(client)

hosts.safe_update("host-XXXXX", name="edge-router-02")
roles.safe_update("role-XXXXX", description="Production web servers")
routes.safe_update("route-XXXXX", router_host_id="host-YYYYY")
tags.safe_update("env:prod", description="Production systems")
networks.safe_update("network-XXXXX", lighthouses_as_relays=False)
```

Explicit empty values are applied; omitted arguments are preserved. Safe
updates are not atomic and can race with another writer between the GET and PUT.

Services also provide focused helpers:

```python
host = hosts.get_by_name("edge-router-02")  # raises when missing
maybe_host = hosts.find_by_name("old-router")  # returns None when missing
route = routes.get_by_name("office")

hosts.add_tag(host["id"], "region:us-central")
hosts.remove_tag(host["id"], "env:staging")
hosts.update_tags(host["id"], ["env:prod", "region:us-central"])

tags.subscribe_route("env:prod", route["id"])
tags.unsubscribe_route("env:prod", route["id"])
prod_tags = tags.find_by_key("env")
```

## Pagination

Resource `list()` methods return one page. Use `list_all` to exhaust a
cursor-paginated endpoint and return a flat list:

```python
from defined_client import list_all

all_hosts = list_all(client.hosts.list, page_size=100)
all_routes = list_all(client.routes.list)
```

Manual pagination is available when page boundaries or metadata matter:

```python
response = client.hosts.list(page_size=25, include_counts=True)
hosts = response["data"]

while response.get("metadata", {}).get("hasNextPage"):
    response = client.hosts.list(
        page_size=25,
        cursor=response["metadata"]["nextCursor"],
    )
    hosts.extend(response["data"])
```

## Error handling

All client exceptions inherit from `DefinedClientError`:

| Exception | Condition |
| --- | --- |
| `ValidationError` | HTTP 400 |
| `AuthenticationError` | HTTP 401 |
| `PermissionDeniedError` | HTTP 403 |
| `NotFoundError` | HTTP 404 |
| `ServerError` | HTTP 5xx |
| `DefinedClientError` | Network errors, invalid JSON, and other API errors |

```python
from defined_client import (
    AuthenticationError,
    DefinedClientError,
    NotFoundError,
    PermissionDeniedError,
    ServerError,
    ValidationError,
)

try:
    host = client.hosts.get("host-XXXXX")
except NotFoundError:
    print("Host not found")
except ValidationError as exc:
    print("Invalid request:", exc.errors)
except (AuthenticationError, PermissionDeniedError):
    print("Check the API key and its scopes")
except ServerError:
    print("Defined Networking returned a server error")
except DefinedClientError as exc:
    print("Request failed:", exc)
```

Exceptions expose `message`, `status_code`, `errors`, and the raw `response`
when one is available.
