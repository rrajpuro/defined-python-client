# Defined Networking API Python Client

A comprehensive Python client for interacting with the [Defined Networking API](https://docs.defined.net/api/defined-networking-api/). This client provides easy-to-use methods for managing hosts, roles, routes, tags, networks, and audit logs.

## Quick Start

### Basic Usage

```python
from defined_client import DefinedClient

# Initialize the client with your API key
api_key = "your-api-key-from-admin.defined.net"
client = DefinedClient(api_key)

# List hosts
hosts = client.hosts.list()

# Create a new host
new_host = client.hosts.create(
    name="My Host",
    network_id="network-XXXXX",
    role_id="role-XXXXX"
)

# Get a specific host
host = client.hosts.get("host-XXXXX")

# Delete a host
client.hosts.delete("host-XXXXX")
```

### Running Directly with `uv`

You can run Python scripts directly from the GitHub repository using `uv` without installing the package:

```bash
uv run --script your_script.py
```

In your Python script, create a file with the following header to specify dependencies:

```python
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "defined-client",
# ]
#
# [tool.uv.sources]
# defined-client = { git = "https://github.com/rrajpuro/defined-python-client" }
# ///

from defined_client import DefinedClient

api_key = "your-api-key-from-admin.defined.net"
with DefinedClient(api_key) as client:
    hosts = client.hosts.list()
    print(hosts)
```

Then run:
```bash
uv run --script your_script.py
```

### Adding to Existing Scripts

To add the `defined-client` dependency to any existing script, use:

```bash
uv add --script your_script.py git+https://github.com/rrajpuro/defined-python-client
```

This will automatically update your script's dependency block with the GitHub repository source.

### Context Manager Usage (Recommended)

Use the context manager to automatically close the session:

```python
from defined_client import DefinedClient

api_key = "your-api-key-from-admin.defined.net"
with DefinedClient(api_key) as client:
    hosts = client.hosts.list()
    new_host = client.hosts.create(name="My Host", network_id="network-XXXXX")
```

## Features

### API Client (`client.hosts`, `client.routes`, etc.)

Thin 1:1 wrappers around every API endpoint:

- **Hosts** — create, list, get, update, delete, block/unblock, enrollment codes, debug commands
- **Roles** — create, list, get, update, delete
- **Routes** — create, list, get, update, delete
- **Tags** — create, list, get, update, delete, priority positioning
- **Networks** — create, list, get, update
- **Audit Logs** — list with filtering by target type and ID
- **Downloads** — get software download links (unauthenticated)

> **Caution:** The API uses full-replacement PUT semantics. Any properties omitted
> from an update request are reset to their default values. Use the service layer
> below to avoid accidental data loss.

### Service Layer (High-Level Convenience)

The service layer sits on top of the API client and handles common patterns:

```python
from defined_client import DefinedClient, HostService, RouteService, TagService, list_all

with DefinedClient(api_key) as client:
    hosts = HostService(client)
    routes = RouteService(client)
    tags = TagService(client)

    # Find resources by name (API only supports lookup by ID)
    host = hosts.get_by_name("web-server-01")       # raises NotFoundError if missing
    host = hosts.find_by_name("web-server-01")       # returns None if missing
    route = routes.get_by_name("Corporate Network")

    # Safe updates — only changes what you pass, preserves everything else
    hosts.safe_update(host["id"], name="web-server-02")
    routes.safe_update(route["id"], router_host_id="host-NEW")

    # Tag helpers
    hosts.add_tag(host["id"], "env:prod")
    hosts.remove_tag(host["id"], "env:staging")
    hosts.update_tags(host["id"], ["env:prod", "region:us-east-1"])

    # Route subscription helpers
    tags.subscribe_route("lab:prod", route["id"])
    tags.unsubscribe_route("lab:prod", route["id"])

    # Find all tags with a given key
    lab_tags = tags.find_by_key("lab")  # returns [{"name": "lab:prod", ...}, ...]

    # Auto-pagination — exhaust all pages of any list endpoint
    all_hosts = list_all(client.hosts.list)
    all_routes = list_all(client.routes.list)
```

## Authentication

Obtain an API key from your Defined Networking admin panel at [https://admin.defined.net/settings/api-keys](https://admin.defined.net/settings/api-keys).

The API key must have the appropriate permission scopes for the operations you want to perform:
- `hosts:` - for host operations
- `roles:` - for role operations
- `routes:` - for route operations
- `tags:` - for tag operations
- `networks:` - for network operations
- `audit-logs:` - for audit log operations

## Error Handling

The client provides specific exception classes for different error scenarios:

```python
from defined_client import (
    DefinedClientError,
    ValidationError,
    AuthenticationError,
    NotFoundError,
    PermissionDeniedError,
    ServerError,
)

try:
    with DefinedClient(api_key) as client:
        client.hosts.get("non-existent-host")
except NotFoundError as e:
    print("Host not found:", e.message)
except ValidationError as e:
    print("Validation error:", e.message)
    print("Error details:", e.errors)
except AuthenticationError as e:
    print("Authentication failed:", e.message)
except PermissionDeniedError as e:
    print("Permission denied:", e.message)
except ServerError as e:
    print("Server error:", e.message)
except DefinedClientError as e:
    print("API error:", e.message)
```

**Notes:**
- List endpoints (e.g., `client.hosts.list()`) return the raw API response which includes pagination metadata under `metadata` as well as the list under `data`.
- Many individual resource methods return the value of the API `data` key; if the server returned no `data` key (or a 204 No Content), the client will return an empty dictionary.

## Pagination

List endpoints support pagination. Use `list_all` to auto-paginate, or paginate manually:

```python
from defined_client import list_all

# Auto-paginate (recommended)
all_hosts = list_all(client.hosts.list)

# Manual pagination
response = client.hosts.list(page_size=10, include_counts=True)
if response['metadata'].get('nextCursor'):
    response = client.hosts.list(cursor=response['metadata']['nextCursor'])
```

## Filtering

Host listing supports various filters:

```python
# List only lighthouses
lighthouses = client.hosts.list(filter_is_lighthouse=True)

# List only relays
relays = client.hosts.list(filter_is_relay=True)

# List blocked hosts
blocked = client.hosts.list(filter_is_blocked=True)

# Filter by role
role_hosts = client.hosts.list(filter_role_id="role-XXXXX")

# Filter by platform
dnclient_hosts = client.hosts.list(filter_metadata_platform="dnclient")
```

## Configuration

The client uses the default API server `https://api.defined.net`. To use a custom server:

```python
client = DefinedClient(
    api_key="your-key",
    base_url="https://custom-api-server.com"
)
```

## Examples

See [examples/example_usage.py](examples/example_usage.py) for comprehensive examples of all available operations.

## API Documentation

For full API documentation, visit: [https://docs.defined.net/api/defined-networking-api/](https://docs.defined.net/api/defined-networking-api/)
