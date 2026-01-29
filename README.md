# Defined Networking API Python Client

A comprehensive Python client for interacting with the [Defined Networking API](https://docs.defined.net/api/defined-networking-api/). This client provides easy-to-use methods for managing hosts, roles, routes, tags, networks, and audit logs.

## Quick Start

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

# Update a host
client.hosts.update("host-XXXXX", name="Updated Name")

# Delete a host
client.hosts.delete("host-XXXXX")
```

## Context Manager Usage (Recommended)

Use the context manager to automatically close the session:

```python
from defined_client import DefinedClient

with DefinedClient(api_key) as client:
    hosts = client.hosts.list()
    new_host = client.hosts.create(name="My Host", network_id="...")
```

## Features

### Hosts Management
- Create, list, get, update, and delete hosts
- Create hosts with enrollment codes in a single request
- Block and unblock hosts
- Send debug commands (StreamLogs, CreateTunnel, PrintTunnel, PrintCert, QueryLighthouse, DebugStack)
- Create enrollment codes

### Roles Management
- Create, list, get, update, and delete roles

### Routes Management
- Create, list, get, update, and delete routes

### Tags Management
- Create, list, get, update, and delete tags
- Set tag priorities with before/after parameters
- Configure config overrides for tags

### Networks Management
- Create, list, get, and update networks

### Audit Logs
- List audit logs with filtering by target type and ID
- Support for pagination

### Downloads
- Get available software download links

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

Notes:
- List endpoints (e.g. ``client.hosts.list()``) return the raw API response which includes
    pagination metadata under ``metadata`` as well as the list under ``data``.
- Many individual resource methods return the value of the API ``data`` key; if the server
    returned no ``data`` key (or a 204 No Content), the client will return an empty dictionary.

## Pagination

List endpoints support pagination:

```python
# Get first page with 10 results
response = client.hosts.list(page_size=10, include_counts=True)

# Get specific page using cursor
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

See [example_usage.py](example_usage.py) for comprehensive examples of all available operations.

## API Documentation

For full API documentation, visit: [https://docs.defined.net/api/defined-networking-api/](https://docs.defined.net/api/defined-networking-api/)
