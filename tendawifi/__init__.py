import logging
import hashlib
import reqtry
import re
from getpass import getpass
logger = logging.getLogger(__name__)


class TendaAC15():
    _AUTH_DATA = {'username': 'admin',
                  'password': ''}

    def __init__(self, url_base='http://192.168.1.1', password=None):
        self._AUTH_DATA["password"] = hashlib.md5(
            str.encode(getpass())).hexdigest() if not password else hashlib.md5(
            str.encode(password)).hexdigest()
        self._URL_BASE = url_base
        self._URLS = {
            'login': self._URL_BASE+'/login/Auth',
            'GetParentControl': self._URL_BASE+'/goform/GetParentControlInfo?mac=',
            'SetParentControl': self._URL_BASE+'/goform/saveParentControlInfo',
            'GetVports': self._URL_BASE+'/goform/GetVirtualServerCfg',
            'SetVports': self._URL_BASE+'/goform/SetVirtualServerCfg',
            'GetNetControl': self._URL_BASE+'/goform/GetNetControlList',
            'SetNetControl': self._URL_BASE+'/goform/SetNetControlList',
            'GetIpMacBind': self._URL_BASE+'/goform/GetIpMacBind',
            'SetIpMacBind': self._URL_BASE+'/goform/SetIpMacBind',
            'GetOnlineList': self._URL_BASE+'/goform/getOnlineList',
            'SysToolReboot': self._URL_BASE+'/goform/SysToolReboot',
            'SetWPS': self._URL_BASE+'/goform/WifiWpsSet',
            'SetupWIFI': self._URL_BASE+'/goform/WifiBasicSet',
            'SetAutoreboot': self._URL_BASE+'/goform/SetSysAutoRebbotCfg',
            'SetSysPass': self._URL_BASE+'/goform/SysToolChangePwd',
            'SetFastInternet': self._URL_BASE+'/goform/fast_setting_internet_set',
            'SetFastRouter': self._URL_BASE+'/goform/fast_setting_wifi_set',
            'GetRouterStatus': self._URL_BASE+'/goform/GetRouterStatus'
        }

    def _get_cookies(self):
        """
        Get cookies to make requests.
        """
        tries = 3
        while tries:
            try:
                cookies = reqtry.post(self._URLS['login'], data=self._AUTH_DATA,
                                      allow_redirects=False, timeout=(5, 5), tries=3, delay=1,
                                      backoff=1.5, jitter=(1, 1.5))
                assert cookies.status_code == 302, f"Invalid http status code: {cookies.status_code}"
                assert bool(cookies.cookies), "Cookies are empty."
                self._cookies = cookies.cookies
                return
            except:
                tries -= 1
                if not tries:
                    self._cookies = None
                    raise

    def _req_get(self, url: str):
        """
        Return a request object of a GET request.
        """
        self._get_cookies()
        if not self._cookies:
            return
        r = reqtry.get(url, cookies=self._cookies, allow_redirects=False, timeout=(3, 3), tries=3, delay=1,
                       backoff=1.5, jitter=(1, 1.5))
        assert r.status_code == 200, f"Get request: Invalid http status code: {r.status_code}"
        return r

    def _get_json(self, url: str) -> dict:
        """
        Return a dictionary from a JSON object of a GET request.
        """
        r = self._req_get(url)
        return r.json() if r else None

    def _req_post(self, url: str, data, raw_res: bool = False):
        """
        Return the POST request response in text format.
        """
        self._get_cookies()
        if not self._cookies:
            return
        r = reqtry.post(url, cookies=self._cookies, data=data, allow_redirects=False, timeout=(3, 3), tries=3, delay=1,
                        backoff=1.5, jitter=(1, 1.5))
        if raw_res:
            return r
        assert r.status_code == 200, f"Post request: Invalid http status code: {r.status_code}"
        assert '"errCode":0' in r.text, f'Post response with error from server. Response: {r.text}'
        return r.text

    def get_parent_control(self, mac: str) -> dict:
        """
        Return a dictionary of a Client Parent Control configuration.
        Args:
            mac:str: Client MAC address ex: "aa:bb:cc:dd:ee:ff"
        Returns:
            dict: {'enable': 1, 'mac': 'aa:bb:cc:dd:ee:ff', 'url_enable': 0, 'urls': '',
                   'time': '09:00-01:30', 'day': '1,1,1,1,1,1,1', 'limit_type': 1}
        """
        return self._get_json(self._URLS['GetParentControl'] + mac)

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
        return self._req_post(self._URLS['SetParentControl'], data={"deviceId": mac, "enable": status, "time": time, "url_enable": 1 if urls_blocked else 0, "urls": urls_blocked, "day": days, "limit_type": 0})

    def get_vports(self) -> dict:
        """
        Return a dictionary of Virtual Server configuration.
        Returns:
            dict: {'lanIp': '192.168.1.1', 'lanMask': '255.255.255.0',
                   'virtualList': [{'ip': '192.168.1.100', 'inPort': '80', 'outPort': '80', 'protocol': '0'}, ...]}
        """
        return self._get_json(self._URLS['GetVports'])

    def set_vports(self, vports_dict: dict) -> str:
        """
        Set Virtual Server configuration from dictionary returned by get_vports() method.
        Args:
            vports_dict:list: List of Virtual Server settings.
        Returns:
            str: Request response '{"errCode":0}'
        """
        if not vports_dict:
            return
        vports_list = []
        for host in vports_dict["virtualList"]:
            vports_list.append(host["ip"] + "," + host["inPort"] +
                               "," + host["outPort"] + "," + host["protocol"])
        return self._req_post(self._URLS['SetVports'], data={
            'list': '~'.join(vports_list)})

    def get_net_control(self) -> list:
        """
        Return a list of Bandwidth configuration.
        Returns:
            list: [{'netControlEn': '1'}, {'upSpeed': '0', 'downSpeed': '0', 'devType': 'unknown',
                    'hostName': 'ClientName', 'ip': '192.168.1.100', 'mac': 'aa:bb:cc:dd:ee:ff', 'limitUp': '0',
                    'limitDown': '0', 'isControled': '0', 'offline': '0', 'isSet': '0'}, ...]
        """
        return self._get_json(self._URLS['GetNetControl'])

    def set_net_control(self, net_control: list) -> str:
        """
        Set Bandwidth Control configuration from list returned by get_net_control() method.
        Args:
            net_control:list: List of Bandwidth settings.
        Returns:
            str: Request response '{"errCode":0}'
        """
        if not net_control:
            return
        net_control_list = ""
        for host in net_control[1:]:
            net_control_list += host["hostName"] + "\r" + host["mac"] + \
                "\r" + host["limitUp"] + "\r" + host["limitDown"] + "\n"
        return self._req_post(self._URLS['SetNetControl'], data={"list": net_control_list})

    def get_ipmac_bind(self) -> dict:
        """
        Return a dictionary of DHCP Reservation configuration.
        Returns:
            dict: {'lanIp': '192.168.1.1', 'lanMask': '255.255.255.0', 'dhttpIP': '172.27.175.218', 'dhcpClientList': [], 
                   'bindList': [{'ipaddr': '192.168.1.100', 'macaddr': 'aa:bb:cc:dd:ee:ff', 'devname': 'ClientName', 'status': '1'}, ...]}
        """
        return self._get_json(self._URLS['GetIpMacBind'])

    def set_ipmac_bind(self, ipmac_bind_dict: dict) -> str:
        """
        Set DHCP Reservation configuration from dictionary returned by get_ipmac_bind() method.
        Args:
            ipmac_bind_dict:dict: List of DHCP Reservation settings.
        Returns:
            str: Request response '{"errCode":0}'
        """
        if not ipmac_bind_dict:
            return
        ipmac_bind = ""
        for host in ipmac_bind_dict["bindList"]:
            ipmac_bind += host["devname"] + "\r" + \
                host["macaddr"] + "\r" + host["ipaddr"] + "\n"
        return self._req_post(self._URLS['SetIpMacBind'], data={"bindnum": str(len(ipmac_bind_dict["bindList"])), "list": ipmac_bind})

    def filter_bindlist_by_devname(self, str_in_dev_name: str) -> list:
        """
        Return a list of DHCP Reservation configuration filtered by 'devname' value if contains the str_in_dev_name param.
        Returns:
            list: [{'ipaddr': '192.168.1.100', 'macaddr': 'aa:bb:cc:dd:ee:ff', 'devname': 'ClientName', 'status': '1'}, ...]}
        """
        mac_list = self.get_ipmac_bind()

        def iterator_func(x):
            if str_in_dev_name.lower() in x["devname"].lower():
                return True
            return False
        return list(filter(iterator_func, mac_list["bindList"]))

    def get_online_list(self) -> list:
        """
        Return a list of online clients.
        Returns:
            list: [{"deviceId": "aa:bb:cc:dd:ee:ff", "ip": "192.168.1.100", "devName": "ClientName", "line": "2", "uploadSpeed": "0",
                    "downloadSpeed": "0", "linkType": "unknown", "black": 0, "isGuestClient": "false" }, ...]}
        """
        return self._get_json(self._URLS['GetOnlineList'])[1:]

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
        online_list = self.get_online_list()

        def iterator_func(x):
            if case_sensitive and (str_in_dev_name in x["devName"]):
                return True
            if not case_sensitive and (str_in_dev_name.lower() in x["devName"].lower()):
                return True
            return False
        return list(filter(iterator_func, online_list))

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
        ip_from, ip_to = int(ip_from), int(ip_to)
        assert ip_from < ip_to, 'Invalid: ip_from must be lower than ip_to. Ex. "ip_from:100, ip_to:150"'
        online_list = self.get_online_list()

        def iterator_func(online_list):
            ip = re.match(
                r"(\d{1,3}.\d{1,3}.\d{1,3}.)(\d{1,3})",  online_list["ip"])
            return True if ip_from <= int(ip[2]) <= ip_to else False
        return list(filter(iterator_func, online_list))

    def reboot(self):
        """
        Reboot the router
        """
        self._get_cookies()
        assert self._cookies, "Reboot failed. It couldn't get the cookies."
        r = reqtry.post(self._URLS['SysToolReboot'], cookies=self._cookies, data={'action': 0}, allow_redirects=False, timeout=(3, 3), tries=3, delay=1,
                        backoff=1.5, jitter=(1, 1.5))
        assert r.status_code == 302, f"Post request: Invalid http status code: {r.status_code}"

    def set_wps_status(self, status: int) -> str:
        """
        Set status of WPS configuration.
        Args:
            status:int: 1 (enable) 0 (disable)
        Returns:
            str: Request response '{"errCode":0}'
        """
        return self._req_post(self._URLS['SetWPS'], data={'wpsEn': status})

    def setup_wifi(self, ssid: str, password: str) -> str:
        """
        Set up WIFI configuration.
        Args:
            ssid:str: WIFI's name ex: "Mywifi"
            password:str: WIFI's password ex: "12345678"
        Returns:
            str: Request response '{"errCode":0}'
        """
        return self._req_post(self._URLS['SetupWIFI'], data={"wrlEn": 1, "wrlEn_5g": 1, "security": "wpawpa2psk", "security_5g": "wpawpa2psk", "ssid": ssid, "ssid_5g": ssid, "hideSsid": 0, "hideSsid_5g": 0, "wrlPwd": password, "wrlPwd_5g": password})

    def set_autoreboot_status(self, status: int) -> str:
        """
        Set status of Scheduled Autoreboot configuration.
        Args:
            status:int: 1 (enable) 0 (disable)
        Returns:
            str: Request response '{"errCode":0}'
        """
        return self._req_post(self._URLS['SetAutoreboot'], data={"autoRebootEn": status, "delayRebootEn": True, "rebootTime": "02: 00"})

    def set_router_password(self, old_pass: str, new_pass: str) -> str:
        """
        Set Router password.
        Args:
            old_pass:str: Old password.
            new_pass:str: New password.
        """
        r = self._req_post(self._URLS['SetSysPass'], data={"GO": "system_password.html", "SYSOPS": hashlib.md5(str.encode(old_pass)).hexdigest(
        ), "SYSPS": hashlib.md5(str.encode(new_pass)).hexdigest(), "SYSPS2": hashlib.md5(str.encode(new_pass)).hexdigest()}, raw_res=True)
        assert "login" in r.headers["Location"], "Incorrect Old Password"

    def set_fast_internet(self, mac: str) -> str:
        """
        Set Fast Internet connection settings.
        Args:
            mac:str: Router MAC address.
        Returns:
            str: Request response '{"errCode":0}'
        """
        data = {
            "netWanType": 0,
            "cloneType": 0,
            "mac": mac,
        }
        return self._req_post(self._URLS['SetFastInternet'], data=data)

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
        data = {
            "ssid": ssid,
            "wrlPassword": wifi_pass,
            "power": "high",
            "timeZone": "-03:00",
            "loginPwd": hashlib.md5(str.encode(router_pass)).hexdigest()
        }
        return self._req_post(self._URLS['SetFastRouter'], data=data)

    def get_router_status(self) -> list:
        """
        Return a dictionary with router information.
        Returns:
            list: {"wl5gEn":"1","wl5gName":"Lajudini","wl24gEn":"1","wl24gName":"Lajudini","lineup":"1|0|0|1","usbNum":"0","clientNum":19,"blackNum":0,"listNum":0,"deviceName":"AC15","lanIP":"192.168.1.1","lanMAC":"CC:2D:21:8F:E4:60","workMode":"router","apStatus":"1310007","wanInfo":[{"wanStatus":"1310007","wanIp":"192.168.0.100","wanUploadSpeed":"20.56","wanDownloadSpeed":"648.83"}],"onlineUpgradeInfo":{"newVersionExist":"0","newVersion":"","curVersion":"V15.03.05.20_multi"}}
        """
        return self._get_json(self._URLS['GetRouterStatus'])
