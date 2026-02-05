"""Example usage of the Defined Networking API client.

This file demonstrates how to use the defined-client Python library to
interact with the Defined Networking API. It covers all major resource
types and common operations.

Get your API key from: https://admin.defined.net/settings/api-keys

For full API documentation, visit: https://docs.defined.net/
"""

from defined_client import (
    DefinedClient,
    DefinedClientError,
    ValidationError,
    AuthenticationError,
    NotFoundError,
    PermissionDeniedError,
    ServerError,
)

# Replace with your actual API key from https://admin.defined.net/settings/api-keys
api_key = "dnkey-your-api-key-here"

# Note: Using context manager is recommended as it automatically closes the session
with DefinedClient(api_key) as client:
    # All examples below assume you're inside this context manager
    print("="*50)
    print("Defined Networking API Client - Example Usage")
    print("="*50 + "\n")

    # Note: Not all examples below are meant to run sequentially.
    # Some create resources that others delete. Pick and choose
    # the examples relevant to your use case.

    # ==================
    # Host Management
    # ==================

    # List all hosts with filters
    hosts_response = client.hosts.list(
        include_counts=True,
        page_size=50,
        filter_is_lighthouse=False,
        filter_role_id="role-PZEDBXHQEXKACJPZ6XOQTIAJA4",
    )
    print("Hosts:", hosts_response)

    # List only lighthouses
    lighthouses = client.hosts.list(filter_is_lighthouse=True)
    print("Lighthouses:", lighthouses)

    # Get a specific host
    host = client.hosts.get("host-24NVITKMNU3CYCEDNFWKAOBX7I")
    print("Host details:", host)

    # Create a regular host
    new_host = client.hosts.create(
        name="app-server-01",
        network_id="network-KAOWMXZHZWCVMGGFKM22XEGYLE",
        role_id="role-PZEDBXHQEXKACJPZ6XOQTIAJA4",
        ip_address="100.100.0.29",
        listen_port=0,  # Auto-assign port
        tags=["env:prod", "region:us-east-1"],
        config_overrides=[
            {"key": "logging.level", "value": "info"},
        ],
    )
    print("Created host:", new_host)

    # Create a lighthouse
    lighthouse = client.hosts.create(
        name="lighthouse-01",
        network_id="network-KAOWMXZHZWCVMGGFKM22XEGYLE",
        static_addresses=["84.123.10.1:4242"],
        listen_port=4242,
        is_lighthouse=True,
        is_relay=False,
    )
    print("Created lighthouse:", lighthouse)

    # Create a relay
    relay = client.hosts.create(
        name="relay-01",
        network_id="network-KAOWMXZHZWCVMGGFKM22XEGYLE",
        listen_port=4242,
        is_lighthouse=False,
        is_relay=True,
    )
    print("Created relay:", relay)

    # Create host with enrollment code in one request
    host_with_code = client.hosts.create_with_enrollment(
        name="web-server-01",
        network_id="network-KAOWMXZHZWCVMGGFKM22XEGYLE",
        role_id="role-PZEDBXHQEXKACJPZ6XOQTIAJA4",
        tags=["env:prod", "app:web"],
    )
    print("Host and enrollment code:", host_with_code)
    print("Enrollment code:", host_with_code.get("enrollmentCode", {}).get("code"))

    # Update a host
    updated_host = client.hosts.update(
        host_id="host-24NVITKMNU3CYCEDNFWKAOBX7I",
        name="app-server-01-updated",
        tags=["env:staging", "region:us-west-2"],
        config_overrides=[
            {"key": "logging.level", "value": "debug"},
        ],
    )
    print("Updated host:", updated_host)

    # Create enrollment code for existing host
    enrollment_code = client.hosts.create_enrollment_code(
        "host-24NVITKMNU3CYCEDNFWKAOBX7I"
    )
    print("Enrollment code:", enrollment_code)
    print("Code:", enrollment_code.get("code"))
    print("Lifetime (seconds):", enrollment_code.get("lifetimeSeconds"))

    # Block a host
    blocked_host = client.hosts.block("host-24NVITKMNU3CYCEDNFWKAOBX7I")
    print("Blocked host:", blocked_host)
    print("Is blocked:", blocked_host.get("isBlocked"))

    # Unblock a host
    unblocked_host = client.hosts.unblock("host-24NVITKMNU3CYCEDNFWKAOBX7I")
    print("Unblocked host:", unblocked_host)
    print("Is blocked:", unblocked_host.get("isBlocked"))

    # Debug commands
    # Stream logs from a host
    logs = client.hosts.debug_command(
        host_id="host-24NVITKMNU3CYCEDNFWKAOBX7I",
        command_type="StreamLogs",
        durationSeconds=10,
        level="debug",
    )
    print("Streaming logs:", logs)

    # Print certificate info
    cert_info = client.hosts.debug_command(
        host_id="host-24NVITKMNU3CYCEDNFWKAOBX7I",
        command_type="PrintCert",
    )
    print("Certificate info:", cert_info)

    # Query lighthouse
    lighthouse_info = client.hosts.debug_command(
        host_id="host-24NVITKMNU3CYCEDNFWKAOBX7I",
        command_type="QueryLighthouse",
    )
    print("Lighthouse info:", lighthouse_info)

    # Delete a host
    deleted = client.hosts.delete("host-24NVITKMNU3CYCEDNFWKAOBX7I")
    print("Deleted host:", deleted)

    # ==================
    # Role Management
    # ==================

    # Create a role with firewall rules
    role = client.roles.create(
        name="Admin",
        description="Administrator role with SSH access",
        firewall_rules=[
            {
                "protocol": "TCP",
                "description": "Allow SSH",
                "allowedRoleID": "role-G3TWUQ4FASQEF44MGMTSRBTYKM",
                "portRange": {"from": 22, "to": 22},
            },
            {
                "protocol": "TCP",
                "description": "Allow HTTPS",
                "allowedRoleID": "role-G3TWUQ4FASQEF44MGMTSRBTYKM",
                "portRange": {"from": 443, "to": 443},
            },
        ],
    )
    print("Created role:", role)

    # List roles with pagination
    roles_response = client.roles.list(page_size=50, include_counts=True)
    print("Roles:", roles_response)

    # Get a specific role
    role = client.roles.get("role-LO4SPDSWTZNJC676WFCZKUB3ZQ")
    print("Role details:", role)

    # Update a role (include all firewall rules or they'll be removed)
    updated_role = client.roles.update(
        role_id="role-LO4SPDSWTZNJC676WFCZKUB3ZQ",
        description="Updated administrator role",
        firewall_rules=[
            {
                "protocol": "TCP",
                "description": "Allow SSH",
                "allowedRoleID": "role-G3TWUQ4FASQEF44MGMTSRBTYKM",
                "portRange": {"from": 22, "to": 22},
            },
        ],
    )
    print("Updated role:", updated_role)

    # Delete a role
    deleted_role = client.roles.delete("role-LO4SPDSWTZNJC676WFCZKUB3ZQ")
    print("Deleted role:", deleted_role)

    # ==================
    # Tag Management
    # ==================

    # Create a tag with config overrides and route subscriptions
    tag = client.tags.create(
        name="env:prod",
        description="Production environment",
        config_overrides=[
            {"key": "logging.level", "value": "info"},
            {"key": "pki.blocklist", "value": "['blocklist.example.com']"},
        ],
        route_subscriptions=["route-X47KHSCOSQJP5IOKNNKRRGHVAI"],
    )
    print("Created tag:", tag)

    # Create a tag with priority positioning
    tag_with_priority = client.tags.create(
        name="region:us-east-1",
        description="US East region",
        after="env:prod",  # Higher priority than env:prod
    )
    print("Created tag with priority:", tag_with_priority)

    # List tags
    tags_response = client.tags.list(page_size=25)
    print("Tags:", tags_response)

    # Get a specific tag
    tag = client.tags.get("env:prod")
    print("Tag details:", tag)

    # Update a tag (include all config overrides or they'll be reset)
    updated_tag = client.tags.update(
        tag="env:prod",
        description="Updated production environment",
        config_overrides=[
            {"key": "logging.level", "value": "warn"},
        ],
        route_subscriptions=["route-X47KHSCOSQJP5IOKNNKRRGHVAI"],
    )
    print("Updated tag:", updated_tag)

    # Delete a tag
    deleted_tag = client.tags.delete("env:prod")
    print("Deleted tag:", deleted_tag)

    # ==================
    # Route Management
    # ==================

    # Create a route
    route = client.routes.create(
        name="Corporate Network",
        description="Route to corporate resources",
        router_host_id="host-24NVITKMNU3CYCEDNFWKAOBX7I",
        routable_cidrs={
            "192.168.1.0/24": {"install": True},
            "10.0.0.0/16": {"install": False},
        },
    )
    print("Created route:", route)

    # List routes
    routes_response = client.routes.list(page_size=10)
    print("Routes:", routes_response)

    # Get a specific route
    route = client.routes.get("route-X47KHSCOSQJP5IOKNNKRRGHVAI")
    print("Route details:", route)

    # Update a route (name is required)
    updated_route = client.routes.update(
        route_id="route-X47KHSCOSQJP5IOKNNKRRGHVAI",
        name="Updated Corporate Network",
        description="Updated route description",
        routable_cidrs={
            "192.168.1.0/24": {"install": True},
        },
    )
    print("Updated route:", updated_route)

    # Delete a route
    deleted_route = client.routes.delete("route-X47KHSCOSQJP5IOKNNKRRGHVAI")
    print("Deleted route:", deleted_route)

    # ==================
    # Network Management
    # ==================

    # Create a network
    network = client.networks.create(
        name="My Network",
        cidr="100.100.0.0/22",
        description="Primary corporate network",
        lighthouses_as_relays=True,
    )
    print("Created network:", network)

    # List networks
    networks_response = client.networks.list(include_counts=True)
    print("Networks:", networks_response)

    # Get a specific network
    network = client.networks.get("network-ZJOW3QUQUX5ZAVPVYRHDQUAEIY")
    print("Network details:", network)

    # Update a network (name is required, CIDR cannot be changed)
    updated_network = client.networks.update(
        network_id="network-ZJOW3QUQUX5ZAVPVYRHDQUAEIY",
        name="Updated Network Name",
        description="Updated network description",
        lighthouses_as_relays=False,
    )
    print("Updated network:", updated_network)

    # ==================
    # Audit Logs
    # ==================

    # List audit logs with pagination
    logs_response = client.audit_logs.list(
        include_counts=True,
        page_size=100,
    )
    print("Audit logs:", logs_response)
    print("Total count:", logs_response.get("metadata", {}).get("totalCount"))

    # Filter by target type
    host_logs = client.audit_logs.list(
        filter_target_type="host",
        page_size=50,
    )
    print("Host-related audit logs:", host_logs)

    # Filter by specific target ID
    specific_logs = client.audit_logs.list(
        filter_target_id="host-24NVITKMNU3CYCEDNFWKAOBX7I",
    )
    print("Logs for specific host:", specific_logs)

    # Filter network changes
    network_logs = client.audit_logs.list(
        filter_target_type="network",
    )
    print("Network-related audit logs:", network_logs)

    # Paginate through audit logs
    first_page = client.audit_logs.list(page_size=10)
    if first_page.get("metadata", {}).get("hasNextPage"):
        next_cursor = first_page.get("metadata", {}).get("nextCursor")
        second_page = client.audit_logs.list(
            cursor=next_cursor,
            page_size=10,
        )
        print("Second page of audit logs:", second_page)

    # ==================
    # Downloads
    # ==================

    # Get download links (unauthenticated endpoint)
    downloads = client.downloads.list()
    print("Downloads:", downloads)

    # Access specific download info
    data = downloads.get("data", {})
    dnclient_latest = data.get("dnclient", {}).get("latest", {})
    print("Latest dnclient for Linux AMD64:", dnclient_latest.get("linux-amd64"))
    print("Latest dnclient for macOS:", dnclient_latest.get("macos-universal-server"))

    # Version info
    version_info = data.get("versionInfo", {})
    print("Latest versions:", version_info.get("latest", {}))


# ==================
# Error Handling Examples
# ==================

print("\n" + "="*50)
print("Error Handling Examples")
print("="*50 + "\n")

# Example 1: Handle NotFoundError
try:
    with DefinedClient(api_key) as client:
        host = client.hosts.get("host-NONEXISTENT")
except NotFoundError as e:
    print(f"NotFoundError: {e.message}")
    print(f"Status code: {e.status_code}")

# Example 2: Handle ValidationError with detailed error info
try:
    with DefinedClient(api_key) as client:
        # Invalid IP address format
        host = client.hosts.create(
            name="test-host",
            network_id="network-KAOWMXZHZWCVMGGFKM22XEGYLE",
            ip_address="999.999.999.999",  # Invalid IP
        )
except ValidationError as e:
    print(f"ValidationError: {e.message}")
    print(f"Status code: {e.status_code}")
    print("Detailed errors:")
    for error in e.errors:
        print(f"  - {error.get('path')}: {error.get('message')} ({error.get('code')})")

# Example 3: Handle AuthenticationError
try:
    with DefinedClient("invalid-api-key") as client:
        hosts = client.hosts.list()
except AuthenticationError as e:
    print(f"AuthenticationError: {e.message}")
    print("Please check your API key at https://admin.defined.net/settings/api-keys")

# Example 4: Handle PermissionDeniedError
try:
    with DefinedClient(api_key) as client:
        # Attempting an operation without required token scope
        host = client.hosts.create(
            name="test-host",
            network_id="network-KAOWMXZHZWCVMGGFKM22XEGYLE",
        )
except PermissionDeniedError as e:
    print(f"PermissionDeniedError: {e.message}")
    print("Your API token lacks the required scope (e.g., 'hosts:create')")

# Example 5: Handle ServerError
try:
    with DefinedClient(api_key) as client:
        # Server errors are rare but should be handled
        hosts = client.hosts.list()
except ServerError as e:
    print(f"ServerError: {e.message}")
    print(f"Status code: {e.status_code}")
    print("Please try again later or contact support")

# Example 6: Catch all API errors
try:
    with DefinedClient(api_key) as client:
        # Any API operation
        hosts = client.hosts.list()
except DefinedClientError as e:
    print(f"API Error: {e.message}")
    print(f"Status code: {e.status_code}")
    if e.errors:
        print("Error details:")
        for error in e.errors:
            print(f"  - {error}")

# Example 7: Best practice - specific to general error handling
def safe_create_host(client, name, network_id, **kwargs):
    """Safely create a host with comprehensive error handling."""
    try:
        host = client.hosts.create(
            name=name,
            network_id=network_id,
            **kwargs
        )
        print(f"Successfully created host: {host.get('id')}")
        return host
    except ValidationError as e:
        print(f"Validation failed: {e}")
        # Handle validation errors (e.g., invalid parameters)
        return None
    except PermissionDeniedError as e:
        print(f"Permission denied: {e}")
        # Handle insufficient permissions
        return None
    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
        # Handle authentication issues
        return None
    except ServerError as e:
        print(f"Server error: {e}")
        # Retry logic could go here
        return None
    except DefinedClientError as e:
        print(f"Unexpected error: {e}")
        # Handle any other API errors
        return None

# Use the safe function
with DefinedClient(api_key) as client:
    host = safe_create_host(
        client,
        name="safe-host",
        network_id="network-KAOWMXZHZWCVMGGFKM22XEGYLE",
        role_id="role-PZEDBXHQEXKACJPZ6XOQTIAJA4",
    )

print("\n" + "="*50)
print("Examples completed!")
print("="*50)
