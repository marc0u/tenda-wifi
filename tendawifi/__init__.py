import json
import logging
import hashlib
import time
import reqtry
from threading import Timer
from getpass import getpass
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
            'SetParentControl': self._URL_BASE+'/goform/parentControlEn',
            'GetVports': self._URL_BASE+'/goform/GetVirtualServerCfg',
            'SetVports': self._URL_BASE+'/goform/SetVirtualServerCfg',
            'GetNetControl': self._URL_BASE+'/goform/GetNetControlList',
            'SetNetControl': self._URL_BASE+'/goform/SetNetControlList',
            'GetIpMacBind': self._URL_BASE+'/goform/GetIpMacBind',
            'SetIpMacBind': self._URL_BASE+'/goform/SetIpMacBind',
            'GetOnlineList': self._URL_BASE+'/goform/getOnlineList',
            'SysToolReboot': self._URL_BASE+'/goform/SysToolReboot'
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

    def _req_post(self, url: str, data):
        """
        Return the POST request response in text format.
        """
        self._get_cookies()
        if not self._cookies:
            return
        r = reqtry.post(url, cookies=self._cookies, data=data, allow_redirects=False, timeout=(3, 3), tries=3, delay=1,
                        backoff=1.5, jitter=(1, 1.5))
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

    def set_parent_control(self, mac: str, status: int) -> str:
        """
        Set status of a Client Parent Control configuration.
        Args:
            mac:str: Client MAC address ex: "aa:bb:cc:dd:ee:ff"
            status:int: Status of client Parent Control ex: 1 (enable) 0 (disable) 
        Returns:
            str: Request response '{"errCode":0}'
        """
        return self._req_post(self._URLS['SetParentControl'], data={'mac': mac, 'isControled': status})

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

    def filter_onlinelist_by_devname(self, str_in_dev_name: str) -> list:
        """
        Return a list of online clients filtered by 'devname' value if contains the str_in_dev_name param.
        Returns:
            list: [{"deviceId": "aa:bb:cc:dd:ee:ff", "ip": "192.168.1.100", "devName": "ClientName", "line": "2", "uploadSpeed": "0",
                    "downloadSpeed": "0", "linkType": "unknown", "black": 0, "isGuestClient": "false" }, ...]}
        """
        online_list = self.get_online_list()

        def iterator_func(x):
            if str_in_dev_name.lower() in x["devName"].lower():
                return True
            return False
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
