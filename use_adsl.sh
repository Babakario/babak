#!/bin/bash

# This script configures the system to use an ADSL modem as the default gateway.
# It requires the network interface name to be provided as a command-line argument.

# Check if the network interface name is provided
if [ -z "$1" ]; then
  echo "Error: Network interface name not provided."
  echo "Usage: $0 <interface_name>"
  exit 1
fi

# Store the interface name
INTERFACE_NAME="$1"

# Define the gateway IP address for the ADSL modem
GATEWAY_ADSL="192.168.1.1"

# Inform the user about sudo requirement
echo "This script requires superuser privileges to modify network routes."
echo "If commands fail, please run the script with sudo."

# Delete the current default route
echo "Deleting current default route..."
if ! ip route del default; then
  echo "Failed to delete default route. Please ensure you are running with sudo."
  exit 1
fi

# Add a new default route using the specified gateway and interface
echo "Adding new default route via $GATEWAY_ADSL on $INTERFACE_NAME..."
if ! ip route add default via "$GATEWAY_ADSL" dev "$INTERFACE_NAME"; then
  echo "Failed to add new default route. Please ensure you are running with sudo and the interface $INTERFACE_NAME exists."
  exit 1
fi

# Print confirmation message
echo "Default gateway set to ADSL modem ($GATEWAY_ADSL via $INTERFACE_NAME)."

exit 0
