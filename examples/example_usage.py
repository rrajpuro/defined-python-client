"""Example usage of the Defined Networking API client"""

from defined_client import DefinedClient, DefinedClientError, ValidationError, AuthenticationError, NotFoundError, PermissionDeniedError, ServerError

# Initialize the client with your API key
api_key = "your-api-key-here"

# Using context manager (recommended)
with DefinedClient(api_key) as client:
    # ==================
    # Host Management
    # ==================

    # List all hosts
    hosts_response = client.hosts.list(include_counts=True)
    print("Hosts:", hosts_response)

    # Get a specific host
    host = client.hosts.get("host-24NVITKMNU3CYCEDNFWKAOBX7I")
    print("Host details:", host)

    # Create a new host
    new_host = client.hosts.create(
        name="My new host",
        network_id="network-KAOWMXZHZWCVMGGFKM22XEGYLE",
        role_id="role-PZEDBXHQEXKACJPZ6XOQTIAJA4",
        ip_address="100.100.0.29",
        listen_port=4242,
        tags=["env:prod", "region:us-east-1"],
    )
    print("Created host:", new_host)

    # Create host with enrollment code in one request
    host_with_code = client.hosts.create_with_enrollment(
        name="Host with enrollment",
        network_id="network-KAOWMXZHZWCVMGGFKM22XEGYLE",
    )
    print("Host and enrollment code:", host_with_code)

    # Update a host
    updated_host = client.hosts.update(
        "host-24NVITKMNU3CYCEDNFWKAOBX7I",
        name="Updated host name",
        tags=["env:staging"],
    )
    print("Updated host:", updated_host)

    # Create enrollment code for a host
    enrollment_code = client.hosts.create_enrollment_code(
        "host-24NVITKMNU3CYCEDNFWKAOBX7I"
    )
    print("Enrollment code:", enrollment_code)

    # Block a host
    blocked = client.hosts.block("host-24NVITKMNU3CYCEDNFWKAOBX7I")
    print("Blocked host:", blocked)

    # Unblock a host
    unblocked = client.hosts.unblock("host-24NVITKMNU3CYCEDNFWKAOBX7I")
    print("Unblocked host:", unblocked)

    # Stream logs from a host
    logs = client.hosts.debug_command(
        "host-24NVITKMNU3CYCEDNFWKAOBX7I",
        "StreamLogs",
        durationSeconds=10,
        level="debug",
    )
    print("Logs:", logs)

    # Delete a host
    deleted = client.hosts.delete("host-24NVITKMNU3CYCEDNFWKAOBX7I")
    print("Deleted host:", deleted)

    # ==================
    # Role Management
    # ==================

    # Create a role
    role = client.roles.create("Admin")
    print("Created role:", role)

    # List roles
    roles_response = client.roles.list()
    print("Roles:", roles_response)

    # Get a specific role
    role = client.roles.get("role-LO4SPDSWTZNJC676WFCZKUB3ZQ")
    print("Role details:", role)

    # Update a role
    updated_role = client.roles.update(
        "role-LO4SPDSWTZNJC676WFCZKUB3ZQ", description="Administrator role"
    )
    print("Updated role:", updated_role)

    # Delete a role
    deleted_role = client.roles.delete("role-LO4SPDSWTZNJC676WFCZKUB3ZQ")
    print("Deleted role:", deleted_role)

    # ==================
    # Tag Management
    # ==================

    # Create a tag
    tag = client.tags.create("env:prod", description="Production environment")
    print("Created tag:", tag)

    # List tags
    tags_response = client.tags.list()
    print("Tags:", tags_response)

    # Get a specific tag
    tag = client.tags.get("env:prod")
    print("Tag details:", tag)

    # Update a tag
    updated_tag = client.tags.update("env:prod", description="Updated description")
    print("Updated tag:", updated_tag)

    # Delete a tag
    deleted_tag = client.tags.delete("env:prod")
    print("Deleted tag:", deleted_tag)

    # ==================
    # Route Management
    # ==================

    # Create a route
    route = client.routes.create("Corporate Network")
    print("Created route:", route)

    # List routes
    routes_response = client.routes.list()
    print("Routes:", routes_response)

    # Get a specific route
    route = client.routes.get("route-X47KHSCOSQJP5IOKNNKRRGHVAI")
    print("Route details:", route)

    # Update a route
    updated_route = client.routes.update("route-X47KHSCOSQJP5IOKNNKRRGHVAI")
    print("Updated route:", updated_route)

    # Delete a route
    deleted_route = client.routes.delete("route-X47KHSCOSQJP5IOKNNKRRGHVAI")
    print("Deleted route:", deleted_route)

    # ==================
    # Network Management
    # ==================

    # Create a network
    network = client.networks.create("My Network", "100.100.0.0/24")
    print("Created network:", network)

    # List networks
    networks_response = client.networks.list()
    print("Networks:", networks_response)

    # Get a specific network
    network = client.networks.get("network-ZJOW3QUQUX5ZAVPVYRHDQUAEIY")
    print("Network details:", network)

    # Update a network
    updated_network = client.networks.update(
        "network-ZJOW3QUQUX5ZAVPVYRHDQUAEIY", name="Updated Network"
    )
    print("Updated network:", updated_network)

    # ==================
    # Audit Logs
    # ==================

    # List audit logs
    logs_response = client.audit_logs.list(include_counts=True)
    print("Audit logs:", logs_response)

    # Filter by target type
    host_logs = client.audit_logs.list(filter_target_type="host")
    print("Host-related audit logs:", host_logs)

    # ==================
    # Downloads
    # ==================

    # Get download links
    downloads = client.downloads.list()
    print("Downloads:", downloads)


# ==================
# Error Handling
# ==================

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
