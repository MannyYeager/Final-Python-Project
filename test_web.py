import http.client
import json
import threading
import unittest
from web import WalletServer


class WalletWebTests(unittest.TestCase):
    def setUp(self):
        self.server = WalletServer(('127.0.0.1', 0))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.cleanup)

    def cleanup(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, path='/api/state', data=None, cookie=None, origin=True, host=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        headers = {'Content-Type': 'application/json'}
        if origin:
            headers['Origin'] = f'http://127.0.0.1:{self.server.server_port}'
        if cookie:
            headers['Cookie'] = cookie
        if host:
            headers['Host'] = host
        connection.request('POST' if data is not None else 'GET', path, json.dumps(data) if data is not None else None, headers)
        response = connection.getresponse()
        text = response.read().decode()
        result = response.status, dict(response.getheaders()), json.loads(text) if 'application/json' in response.getheader('Content-Type') else text
        connection.close()
        return result

    def session(self):
        return self.request()[1]['Set-Cookie'].split(';')[0]

    def test_transaction_flow_and_history(self):
        cookie = self.session()
        status, _, result = self.request('/api/transaction', {'kind': 'deposit', 'currency': 'USD', 'amount': '10'}, cookie)
        self.assertEqual(status, 200)
        self.assertEqual(result['state']['balance'], '114.80')
        _, _, result = self.request('/api/transaction', {'kind': 'withdraw', 'currency': 'GHS', 'amount': '25'}, cookie)
        self.assertEqual(result['state']['balance'], '89.80')
        _, _, result = self.request('/api/transaction', {'kind': 'withdraw_all', 'currency': 'EURO'}, cookie)
        self.assertEqual(result['state']['balance'], '0.00')
        self.assertEqual(len(result['state']['history']), 3)
        self.assertEqual(result['state']['history'][0]['kind'], 'withdraw_all')

    def test_invalid_transactions_preserve_balance_and_history(self):
        cookie = self.session()
        self.request('/api/transaction', {'kind': 'deposit', 'currency': 'GHS', 'amount': '100'}, cookie)
        for payload in [dict(kind='withdraw', currency='GHS', amount='101'),
                        dict(kind='withdraw_all', currency='BAD'),
                        dict(kind='deposit', currency='GHS', amount='NaN'),
                        dict(kind='deposit', currency='GHS', amount='abc'),
                        dict(kind='deposit', currency='GHS', amount=[]),
                        dict(kind='transfer', currency='GHS', amount='1'),
                        dict(kind=[], currency='GHS', amount='1')]:
            with self.subTest(payload=payload):
                self.assertEqual(self.request('/api/transaction', payload, cookie)[0], 400)
                state = self.request(cookie=cookie)[2]
                self.assertEqual(state['balance'], '100.00')
                self.assertEqual(len(state['history']), 1)

    def test_browser_sessions_are_separate(self):
        first, second = self.session(), self.session()
        self.request('/api/transaction', {'kind': 'deposit', 'currency': 'GHS', 'amount': '100'}, first)
        self.assertEqual(self.request(cookie=second)[2]['balance'], '0.00')
        self.assertIn('HttpOnly', self.request()[1]['Set-Cookie'])

    def test_static_assets_and_request_boundaries(self):
        self.assertIn('Five possibilities', self.request('/')[2])
        for path in ['/app.js', '/ui.js', '/ui.css', '/theme.css', '/workspace.css', '/vendor/anime.umd.min.js']:
            status, headers, body = self.request(path)
            self.assertEqual(status, 200)
            self.assertGreater(len(body), 100)
            self.assertIn("script-src 'self'", headers['Content-Security-Policy'])
        self.assertEqual(self.request('/api/transaction', {}, origin=False)[0], 403)
        self.assertEqual(self.request(host='untrusted.example')[0], 403)
        self.assertEqual(self.request('/../wallet.py')[0], 404)

    def test_market_route_is_validated_and_offline_history_is_explicit(self):
        status, _, result=self.request('/api/market?base=USD&quote=GHS&days=7')
        self.assertEqual(status,200)
        self.assertEqual(result['points'],[])
        self.assertTrue(result['error'])
        self.assertEqual(self.request('/api/market?base=BAD&quote=GHS&days=30')[0],400)
        self.assertEqual(self.request('/api/market?base=USD&quote=GHS&days=999')[0],400)


if __name__ == '__main__':
    unittest.main()
