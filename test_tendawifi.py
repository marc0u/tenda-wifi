import pytest
import reqtry
import tendawifi
import hashlib


URL_BASE = 'http://localhost'
URLS = {
    'login': URL_BASE+'/login/Auth',
    'GetParentControl': URL_BASE+'/goform/GetParentControlInfo?mac=',
    'SetParentControl': URL_BASE+'/goform/saveParentControlInfo',
    'GetVports': URL_BASE+'/goform/GetVirtualServerCfg',
    'SetVports': URL_BASE+'/goform/SetVirtualServerCfg',
    'GetNetControl': URL_BASE+'/goform/GetNetControlList',
    'SetNetControl': URL_BASE+'/goform/SetNetControlList',
    'GetIpMacBind': URL_BASE+'/goform/GetIpMacBind',
    'SetIpMacBind': URL_BASE+'/goform/SetIpMacBind',
    'GetOnlineList': URL_BASE+'/goform/getOnlineList',
    'SysToolReboot': URL_BASE+'/goform/SysToolReboot',
    'SetWPS': URL_BASE+'/goform/WifiWpsSet',
    'SetupWIFI': URL_BASE+'/goform/WifiBasicSet',
    'SetAutoreboot': URL_BASE+'/goform/SetSysAutoRebbotCfg',
    'SetSysPass': URL_BASE+'/goform/SysToolChangePwd',
}

RESP = {
    'GetParentControl': {'enable': 1, 'mac': 'aa:bb:cc:dd:ee:ff', 'url_enable': 0, 'urls': '',
                         'time': '09:00-01:30', 'day': '1,1,1,1,1,1,1', 'limit_type': 1},
    "GetVports": {'lanIp': '192.168.1.1', 'lanMask': '255.255.255.0',
                  'virtualList': [{'ip': '192.168.1.100', 'inPort': '80', 'outPort': '80', 'protocol': '0'}, {'ip': '192.168.1.100', 'inPort': '80', 'outPort': '80', 'protocol': '0'}]},
    "GetNetControl": [{'netControlEn': '1'}, {'upSpeed': '0', 'downSpeed': '0', 'devType': 'unknown',
                                              'hostName': 'ClientName', 'ip': '192.168.1.100', 'mac': 'aa:bb:cc:dd:ee:ff', 'limitUp': '0',
                                              'limitDown': '0', 'isControled': '0', 'offline': '0', 'isSet': '0'}, {'upSpeed': '0', 'downSpeed': '0', 'devType': 'unknown',
                                                                                                                    'hostName': 'ClientName', 'ip': '192.168.1.100', 'mac': 'aa:bb:cc:dd:ee:ff', 'limitUp': '0',
                                                                                                                    'limitDown': '0', 'isControled': '0', 'offline': '0', 'isSet': '0'}],
    "GetIpMacBind": {'lanIp': '192.168.1.1', 'lanMask': '255.255.255.0', 'dhttpIP': '172.27.175.218', 'dhcpClientList': [],
                     'bindList': [{'ipaddr': '192.168.1.100', 'macaddr': 'aa:bb:cc:dd:ee:ff', 'devname': 'ClientName1', 'status': '1'}, {'ipaddr': '192.168.1.100', 'macaddr': 'aa:bb:cc:dd:ee:ff', 'devname': 'ClientName2', 'status': '1'}]},
    "GetOnlineList": [None, {"deviceId": "aa:bb:cc:dd:ee:ff", "ip": "192.168.1.100", "devName": "ClientName1", "line": "2", "uploadSpeed": "0",
                             "downloadSpeed": "0", "linkType": "unknown", "black": 0, "isGuestClient": "false"}, {"deviceId": "aa:bb:cc:dd:ee:ff", "ip": "192.168.1.100", "devName": "ClientName2", "line": "2", "uploadSpeed": "0",
                                                                                                                  "downloadSpeed": "0", "linkType": "unknown", "black": 0, "isGuestClient": "false"}]
}

# custom class to be the mock return value of requests.get()


class MockGetResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


class MockPostResponse:
    def __init__(self, has_cookies, status_code, text=None, headers=None):
        self.cookies = has_cookies
        self.status_code = status_code
        self.text = text
        self.headers = headers


@ pytest.fixture
def mock_response(monkeypatch):
    def mock_reqtry_get(*args, **kwargs):
        if args[0] == "http://test.com":
            return MockGetResponse({"success": True}, 200)
        if args[0] == URLS["GetParentControl"] + 'aa:bb:cc:dd:ee:ff':
            return MockGetResponse(RESP["GetParentControl"], 200)
        elif args[0] == URLS["GetVports"]:
            return MockGetResponse(RESP["GetVports"], 200)
        elif args[0] == URLS["GetNetControl"]:
            return MockGetResponse(RESP["GetNetControl"], 200)
        elif args[0] == URLS["GetIpMacBind"]:
            return MockGetResponse(RESP["GetIpMacBind"], 200)
        elif args[0] == URLS["GetOnlineList"]:
            return MockGetResponse(RESP["GetOnlineList"], 200)
        return MockGetResponse(None, 404)

    def mock_reqtry_post(*args, **kwargs):
        if args[0] == URLS["login"]:
            return MockPostResponse(True, 302)
        if args[0] == URLS["SetParentControl"] and kwargs["data"] == {"deviceId": 'aa:bb:cc:dd:ee:ff', "enable": 1, "time": "06:00-06:05", "url_enable": 0, "urls": "", "day": "1,1,1,1,1,1,1", "limit_type": 0}:
            return MockPostResponse(True, 200, '"errCode":0')
        if args[0] == URLS["SetVports"] and kwargs["data"] == {'list': '192.168.1.100,80,80,0~192.168.1.100,80,80,0'}:
            return MockPostResponse(True, 200, '"errCode":0')
        if args[0] == URLS["SetNetControl"]:
            return MockPostResponse(True, 200, '"errCode":0')
        if args[0] == URLS["SetIpMacBind"]:
            return MockPostResponse(True, 200, '"errCode":0')
        if args[0] == URLS["SysToolReboot"]:
            return MockPostResponse(True, 302)
        if args[0] == URLS["SetWPS"] and kwargs["data"] == {'wpsEn': 1}:
            return MockPostResponse(True, 200, '"errCode":0')
        if args[0] == URLS["SetupWIFI"] and kwargs["data"] == {"wrlEn": 1, "wrlEn_5g": 1, "security": "wpawpa2psk", "security_5g": "wpawpa2psk", "ssid": "Mywifi", "ssid_5g": "Mywifi", "hideSsid": 0, "hideSsid_5g": 0, "wrlPwd": "12345678", "wrlPwd_5g": "12345678"}:
            return MockPostResponse(True, 200, '"errCode":0')
        if args[0] == URLS["SetAutoreboot"] and kwargs["data"] == {"autoRebootEn": 1, "delayRebootEn": True, "rebootTime": "02: 00"}:
            return MockPostResponse(True, 200, '"errCode":0')
        if args[0] == URLS["SetSysPass"] and kwargs["data"] == {"GO": "system_password.html", "SYSOPS": hashlib.md5(str.encode("1234")).hexdigest(), "SYSPS": hashlib.md5(str.encode("1234")).hexdigest(), "SYSPS2": hashlib.md5(str.encode("1234")).hexdigest()}:
            return MockPostResponse(True, 302, headers={"Location": "login"})
        return MockPostResponse(None, 404)

    monkeypatch.setattr(reqtry, "get", mock_reqtry_get)
    monkeypatch.setattr(reqtry, "post", mock_reqtry_post)


@ pytest.fixture
def tenda():
    return tendawifi.TendaAC15("http://localhost", "1234")


def test_req_tools(mock_response, tenda):
    tenda._get_cookies()
    assert tenda._cookies
    r = tenda._req_get("http://test.com")
    assert r.status_code == 200
    r = tenda._get_json("http://test.com")
    assert r["success"]


def test_get_parent_control(mock_response, tenda):
    r = tenda.get_parent_control('aa:bb:cc:dd:ee:ff')
    assert r == RESP["GetParentControl"]


def test_set_parent_control(mock_response, tenda):
    r = tenda.set_parent_control('aa:bb:cc:dd:ee:ff', 1)
    assert r == '"errCode":0'


def test_get_vports(mock_response, tenda):
    r = tenda.get_vports()
    assert r == RESP["GetVports"]


def test_set_vports(mock_response, tenda):
    r = tenda.set_vports(tenda.get_vports())
    assert r == '"errCode":0'


def test_get_net_control(mock_response, tenda):
    r = tenda.get_net_control()
    assert r == RESP["GetNetControl"]


def test_set_net_control(mock_response, tenda):
    r = tenda.set_net_control(tenda.get_net_control())
    assert r == '"errCode":0'


def test_get_ipmac_bind(mock_response, tenda):
    r = tenda.get_ipmac_bind()
    assert r == RESP["GetIpMacBind"]


def test_set_imac_bind(mock_response, tenda):
    r = tenda.set_ipmac_bind(tenda.get_ipmac_bind())
    assert r == '"errCode":0'


def test_filter_bindlist_by_devname(mock_response, tenda):
    r = tenda.filter_bindlist_by_devname("clientname1")
    assert len(r) == 1
    r = tenda.filter_bindlist_by_devname("clientname")
    assert len(r) == 2
    for i in r:
        assert "clientname" in i["devname"].lower()


def test_get_online_list(mock_response, tenda):
    r = tenda.get_online_list()
    assert r == RESP["GetOnlineList"][1:]


def test_filter_onlinelist_by_devname(mock_response, tenda):
    r = tenda.filter_onlinelist_by_devname("clientname1")
    assert len(r) == 1
    r = tenda.filter_onlinelist_by_devname("clientname")
    assert len(r) == 2
    for i in r:
        assert "clientname" in i["devName"].lower()


def test_reboot(mock_response, tenda):
    tenda.reboot()


def test_set_wps(mock_response, tenda):
    r = tenda.set_wps_status(1)
    assert r == '"errCode":0'


def test_set_wps(mock_response, tenda):
    r = tenda.set_wps_status(1)
    assert r == '"errCode":0'


def test_setup_wifi(mock_response, tenda):
    r = tenda.setup_wifi("Mywifi", "12345678")
    assert r == '"errCode":0'


def test_set_autoreboot(mock_response, tenda):
    r = tenda.set_autoreboot_status(1)
    assert r == '"errCode":0'


def test_set_password(mock_response, tenda):
    tenda.set_router_password("1234", "1234")
