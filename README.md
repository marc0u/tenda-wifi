# tenda-wifi

A simple Python package that allows to manage tenda router AC15.

## Installation

```bash
    $ pip install tendawifi
```

## API

First of all, it has to instance a TendaAC15 object:

If it run with default router ip "192.168.1.1":

```python
>>> t = tendawifi.TendaAC15()
>>> Password:
```

If it run with custom router ip:

```python
>>> t = tendawifi.TendaAC15(url_base="10.0.0.1")
>>> Password:
```

If it run without asking the password:

```python
>>> t = tendawifi.TendaAC15(url_base="10.0.0.1", password="YOURPASS")
```

Currently, it has the following features:

### Get Parent Control configuration by MAC address

```python
def get_parent_control(self, mac: str) -> dict:
    """
    Return a dictionary of a Client Parent Control configuration.
    Args:
        mac:str: Client MAC address ex: "aa:bb:cc:dd:ee:ff"
    Returns:
        dict: {'enable': 1, 'mac': 'aa:bb:cc:dd:ee:ff', 'url_enable': 0, 'urls': '',
        'time': '09:00-01:30', 'day': '1,1,1,1,1,1,1', 'limit_type': 1}
    """
```

### Set Parent Control configuration MAC address

```python
def set_parent_control(self, mac: str, status: int, time: str = "06:00-06:05", days: str = "1,1,1,1,1,1,1", urls_blocked: str = "") -> str:
    """
    Set status of a Client Parent Control configuration.
    Args:
        mac:str: Client MAC address ex: "aa:bb:cc:dd:ee:ff"
        status:int: Status of client Parent Control ex: 1 (enable) 0 (disable) 
        time:str: Time between is allowed. ex: "06:00-06:05"
        days:str: Week days between is allowed. ex: "1,1,1,1,1,1,1"
        urls_blocked:str: List of blocked urls. ex: "xvideos,pornhub"
    Returns:
        str: Request response '{"errCode":0}'
    """
```

### Get Virtual Server configuration

```python
def get_vports(self) -> dict:
    """
    Return a dictionary of Virtual Server configuration.
    Returns:
        dict: {'lanIp': '192.168.1.1', 'lanMask': '255.255.255.0',
            'virtualList': [{'ip': '192.168.1.100', 'inPort': '80', 'outPort': '80', 'protocol': '0'}, ...]}
    """
```

### Set Virtual Server configuration

```python
def set_vports(self, vports_dict: dict) -> str:
    """
    Set Virtual Server configuration from dictionary returned by get_vports() method.
    Args:
        vports_dict:list: List of Virtual Server settings.
    Returns:
        str: Request response '{"errCode":0}'
    """
```

### Get Bandwidth Control configuration

```python
def get_net_control(self) -> list:
    """
    Return a list of Bandwidth configuration.
    Returns:
        list: [{'netControlEn': '1'}, {'upSpeed': '0', 'downSpeed': '0', 'devType': 'unknown',
            'hostName': 'ClientName', 'ip': '192.168.1.100', 'mac': 'aa:bb:cc:dd:ee:ff', 'limitUp': '0',
            'limitDown': '0', 'isControled': '0', 'offline': '0', 'isSet': '0'}, ...]
        """
```

### Set Bandwidth Control configuration

```python
def set_net_control(self, net_control: list) -> str:
    """
    Set Bandwidth Control configuration from list returned by get_net_control() method.
    Args:
        net_control:list: List of Bandwidth settings.
    Returns:
        str: Request response '{"errCode":0}'
    """
```

### Get DHCP Reservation configuration by MAC address

```python
def get_ipmac_bind(self) -> dict:
    """
    Return a dictionary of DHCP Reservation configuration.
    Returns:
        dict: {'lanIp': '192.168.1.1', 'lanMask': '255.255.255.0', 'dhttpIP': '172.27.175.218', 'dhcpClientList': [],
            'bindList': [{'ipaddr': '192.168.1.100', 'macaddr': 'aa:bb:cc:dd:ee:ff', 'devname': 'ClientName', 'status': '1'}, ...]}
    """
```

### Set DHCP Reservation configuration by MAC address

```python
def set_ipmac_bind(self, ipmac_bind_dict: dict) -> str:
    """
    Set DHCP Reservation configuration from dictionary returned by get_ipmac_bind() method.
    Args:
        ipmac_bind_dict:dict: List of DHCP Reservation settings.
    Returns:
        str: Request response '{"errCode":0}'
    """
```

### Filter DHCP Reservation configuration by 'devname' value

```python
def filter_bindlist_by_devname(self, str_in_dev_name: str) -> list:
    """
    Return a list of DHCP Reservation configuration filtered by 'devname' value if contains the str_in_dev_name param.
    Returns:
        list: [{'ipaddr': '192.168.1.100', 'macaddr': 'aa:bb:cc:dd:ee:ff', 'devname': 'ClientName', 'status': '1'}, ...]}
    """
```

### Get online clients list

```python
def get_online_list(self) -> list:
    """
    Return a list of online clients.
    Returns:
        list: [{"deviceId": "aa:bb:cc:dd:ee:ff", "ip": "192.168.1.100", "devName": "ClientName", "line": "2", "uploadSpeed": "0",
                "downloadSpeed": "0", "linkType": "unknown", "black": 0, "isGuestClient": "false" }, ...]}
    """
```

### Filter online clients list by 'devName' value

```python
def filter_onlinelist_by_devname(self, str_in_dev_name: str, case_sensitive=True) -> list:
    """
    Return a list of online clients filtered by 'devname' value if contains the str_in_dev_name param.
    Args:
        str_in_dev_name: String to find in devname. ex: "someone"
        case_sensitive:bool: Whether to filter with case sensitive parameter.
    Returns:
        list: [{"deviceId": "aa:bb:cc:dd:ee:ff", "ip": "192.168.1.100", "devName": "ClientName", "line": "2", "uploadSpeed": "0",
                "downloadSpeed": "0", "linkType": "unknown", "black": 0, "isGuestClient": "false" }, ...]}
    """
```

### Filter online clients list by ip range

```python
def filter_onlinelist_by_iprange(self, ip_from: int, ip_to: int) -> list:
    """
    Return a list of online clients filtered by 'ip'.
    Args:
        ip_from:str: IP from ex: 100
        ip_to:str: IP to ex: 250
    Returns:
        list: [{"deviceId": "aa:bb:cc:dd:ee:ff", "ip": "192.168.1.100", "devName": "ClientName", "line": "2", "uploadSpeed": "0",
                "downloadSpeed": "0", "linkType": "unknown", "black": 0, "isGuestClient": "false" }, ...]}
    """
```

### Reboot the router

```python
def reboot(self):
    """
    Reboot the router
    """
```

### Set WPS status

```python
def set_wps_status(self, status: int) -> str:
    """
    Set status of WPS configuration.
    Args:
        status:int: 1 (enable) 0 (disable)
    Returns:
        str: Request response '{"errCode":0}'
    """
```

### Setup WIFI

```python
def setup_wifi(self, ssid: str, password: str) -> str:
    """
    Set up WIFI configuration.
    Args:
        ssid:str: WIFI's name ex: "Mywifi"
        password:str: WIFI's password ex: "12345678"
    Returns:
        str: Request response '{"errCode":0}'
    """
```

### Set Scheduled Autoreboot status 

```python
def set_autoreboot_status(self, status: int) -> str:
    """
    Set status of Scheduled Autoreboot configuration.
    Args:
        status:int: 1 (enable) 0 (disable)
    Returns:
        str: Request response '{"errCode":0}'
    """
```

### Set Router password 

```python
def set_router_password(self, old_pass: str, new_pass: str) -> str:
    """
    Set Router password.
    Args:
        old_pass:str: Old password.
        new_pass:str: New password.
    """
```

### Set initial Internet settings 

```python
def set_fast_internet(self, mac: str) -> str:
    """
    Set Fast Internet connection settings.
    Args:
        mac:str: Router MAC address.
    Returns:
        str: Request response '{"errCode":0}'
    """
```

### Set initial Router settings 

```python
def set_fast_router(self, ssid: str, wifi_pass: str, router_pass: str) -> str:
    """
    Set Fast Router settings.
    Args:
        ssid:str: WIFI's name ex: "Mywifi"
        wifi_pass:str: WIFI's password ex: "12345678"
        router_pass:str: Router's password ex: "12345678"
    Returns:
        str: Request response '{"errCode":0}'
    """
```