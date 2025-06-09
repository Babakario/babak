# Linux Network Switching Scripts

These scripts allow you to quickly switch between two different network configurations by changing the IP address, default gateway, and DNS settings for a specified network interface. This is the Linux equivalent of the Windows batch scripts provided in the original request.

**Disclaimer:** Modifying network configurations typically requires root privileges. You will likely need to run these scripts with `sudo`. These scripts attempt to use NetworkManager (`nmcli`) first, and fall back to using `ip` commands if `nmcli` is not available. Changes made with `ip` commands might not persist across reboots or if NetworkManager subsequently manages the interface.

## Scripts

- `switch_to_adsl.sh`: Configures the network interface for an ADSL modem (assumed Gateway: 192.168.1.1, DNS: 8.8.8.8).
- `switch_to_irancell.sh`: Configures the network interface for an Irancell modem (assumed Gateway: 192.168.1.2, DNS: 8.8.4.4).

## Prerequisites

1.  **Identify your Network Interface Name:**
    You need to know the name of the network interface you want to configure (e.g., `eth0`, `enp3s0`, `wlan0`). You can find this using one of the following commands:
    ```bash
    ip link show
    ```
    or
    ```bash
    nmcli device status
    ```
    Look for the interface that corresponds to your Ethernet or Wi-Fi connection.

2.  **Make Scripts Executable:**
    Before running the scripts for the first time, make them executable:
    ```bash
    chmod +x switch_to_adsl.sh
    chmod +x switch_to_irancell.sh
    ```

## Usage

To switch your network configuration, run the desired script with `sudo` and pass the network interface name as the first argument.

**Example:**

If your network interface is `eth0`:

-   To switch to ADSL:
    ```bash
    sudo ./switch_to_adsl.sh eth0
    ```

-   To switch to Irancell:
    ```bash
    sudo ./switch_to_irancell.sh eth0
    ```

The scripts will attempt to find an existing NetworkManager connection profile for the given interface. If found, it will modify this profile. If NetworkManager is not used or the profile isn't found, it will fall back to using `ip` commands (which might have non-persistent effects).

## Using DHCP (Dynamic IP Configuration)

If you prefer your interface to obtain IP, gateway, and DNS information automatically via DHCP (instead of the static IPs defined in these scripts), you can configure this using `nmcli` (if available).

1.  **Find your connection name** (similar to how the script does it, or use `nmcli con show`). Let's say it's `MyConnection`.
2.  **Set the connection to DHCP for IPv4:**
    ```bash
    sudo nmcli con mod MyConnection ipv4.method auto ipv4.gateway "" ipv4.dns ""
    ```
    (Clearing gateway and DNS explicitly might be needed if previously set manually).
3.  **Reactivate the connection:**
    ```bash
    sudo nmcli con down MyConnection && sudo nmcli con up MyConnection
    ```

If you are not using NetworkManager, configuring DHCP typically involves:
- Ensuring a DHCP client (like `dhclient` or `dhcpcd`) is installed and running.
- Modifying network configuration files (e.g., `/etc/network/interfaces` on Debian/Ubuntu, or files in `/etc/sysconfig/network-scripts/` on RHEL/CentOS) to specify DHCP for the interface. The exact method varies by Linux distribution. For example, in `/etc/network/interfaces`:
  ```
  auto eth0
  iface eth0 inet dhcp
  ```

## Customization

You can modify the `IP_ADDRESS`, `GATEWAY`, and `DNS_SERVER` variables at the beginning of each script to match your specific network requirements.
