#!/bin/bash

# This script configures the system to use an Irancell modem as the default gateway.
# It requires the network interface name to be provided as a command-line argument.

# Check if the network interface name is provided
if [ -z "$1" ]; then
  echo "Error: Network interface name not provided."
  echo "Usage: $0 <interface_name>"
  exit 1
fi

# Store the interface name
INTERFACE_NAME="$1"

# Define the gateway IP address for the Irancell modem
GATEWAY_IRANCELL="192.168.1.2"

# Inform the user about sudo requirement
echo "This script requires superuser privileges to modify network routes."
echo "If commands fail, please run the script with sudo."

# Delete the current default route
echo "Deleting current default route..."
if ! ip route del default; then
  echo "Failed to delete default route. Please ensure you are running with sudo."
  # It's possible the default route doesn't exist, which isn't a fatal error for this script's purpose.
  # We'll proceed to add the new route. If there was a *different* issue, the next command will likely fail.
  echo "Continuing to add new route..."
fi

# Add a new default route using the specified gateway and interface
echo "Adding new default route via $GATEWAY_IRANCELL on $INTERFACE_NAME..."
if ! ip route add default via "$GATEWAY_IRANCELL" dev "$INTERFACE_NAME"; then
  echo "Failed to add new default route. Please ensure you are running with sudo and the interface $INTERFACE_NAME exists."
  exit 1
fi

# Print confirmation message
echo "Default gateway set to Irancell modem ($GATEWAY_IRANCELL via $INTERFACE_NAME)."

exit 0
