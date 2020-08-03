import pytest
import reqtry
import tendawifi


URL_BASE = 'http://localhost'
URLS = {
    'login': URL_BASE+'/login/Auth',
    'GetParentControl': URL_BASE+'/goform/GetParentControlInfo?mac=',
    'SetParentControl': URL_BASE+'/goform/parentControlEn',
    'GetVports': URL_BASE+'/goform/GetVirtualServerCfg',
    'SetVports': URL_BASE+'/goform/SetVirtualServerCfg',
    'GetNetControl': URL_BASE+'/goform/GetNetControlList',
    'SetNetControl': URL_BASE+'/goform/SetNetControlList',
    'GetIpMacBind': URL_BASE+'/goform/GetIpMacBind',
    'SetIpMacBind': URL_BASE+'/goform/SetIpMacBind'
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
                     'bindList': [{'ipaddr': '192.168.1.100', 'macaddr': 'aa:bb:cc:dd:ee:ff', 'devname': 'ClientName', 'status': '1'}, {'ipaddr': '192.168.1.100', 'macaddr': 'aa:bb:cc:dd:ee:ff', 'devname': 'ClientName', 'status': '1'}]}

}

# custom class to be the mock return value of requests.get()


class MockGetResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


class MockPostResponse:
    def __init__(self, has_cookies, status_code):
        self.cookies = has_cookies
        self.status_code = status_code


@pytest.fixture
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
        return MockGetResponse(None, 404)

    def mock_reqtry_post(*args, **kwargs):
        if args[0] == URLS["login"]:
            return MockPostResponse(True, 302)
        return MockPostResponse(None, 404)

    monkeypatch.setattr(reqtry, "get", mock_reqtry_get)
    monkeypatch.setattr(reqtry, "post", mock_reqtry_post)


@pytest.fixture
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


def test_get_vports(mock_response, tenda):
    r = tenda.get_vports()
    assert r == RESP["GetVports"]


def test_get_net_control(mock_response, tenda):
    r = tenda.get_net_control()
    assert r == RESP["GetNetControl"]


def test_get_ipmac_bind(mock_response, tenda):
    r = tenda.get_ipmac_bind()
    assert r == RESP["GetIpMacBind"]
