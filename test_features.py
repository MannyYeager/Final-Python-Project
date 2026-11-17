import unittest
from decimal import Decimal
from exchange import RateService
from web import WalletServer, initial_session


class FeatureTests(unittest.TestCase):
    def setUp(self):
        self.server = WalletServer(('127.0.0.1', 0))
        self.addCleanup(self.server.server_close)
        self.data = initial_session()

    def test_review_is_atomic_idempotent_and_records_method(self):
        payload = dict(kind='deposit', currency='USD', amount='10', method_id='mobile-demo', note='Travel fund')
        self.server.action('/api/quote', payload, self.data)
        quote = self.data['pending_quote']
        self.assertEqual(self.data['wallet'].balance, 0)
        self.server.action('/api/transaction', {'quote_id': quote['id']}, self.data)
        self.server.action('/api/transaction', {'quote_id': quote['id']}, self.data)
        self.assertEqual(self.data['wallet'].balance, Decimal('114.80'))
        self.assertEqual(len(self.data['history']), 1)
        self.assertEqual(self.data['history'][0]['method']['type'], 'mobile')
        self.assertIn('Travel fund', self.server.export(self.data)[0])

    def test_expired_quote_balance_changes_and_missing_method_rejected(self):
        payload = dict(kind='deposit', currency='GHS', amount='10')
        self.server.action('/api/quote', payload, self.data)
        quote = self.data['pending_quote']
        quote['expires'] = 0
        with self.assertRaises(ValueError): self.server.action('/api/transaction', {'quote_id':quote['id']}, self.data)
        self.server.action('/api/quote', payload, self.data)
        quote = self.data['pending_quote']
        self.data['wallet'].balance = Decimal(1)
        with self.assertRaises(ValueError): self.server.action('/api/transaction', {'quote_id':quote['id']}, self.data)
        with self.assertRaises(ValueError): self.server.action('/api/quote', {**payload,'method_id':'missing'}, self.data)
        self.assertEqual(self.data['history'], [])

    def test_method_validation_preferences_and_goal(self):
        self.server.action('/api/method',dict(type='bank',label='Future demo',suffix='1234'),self.data)
        self.assertEqual(len(self.data['methods']),4)
        for suffix in ['1234567890123456','12a4','１２３４']:
            with self.assertRaises(ValueError): self.server.action('/api/method',dict(type='card',label='Demo',suffix=suffix),self.data)
        self.server.action('/api/preferences',{'view_currency':'EUR'},self.data)
        self.assertEqual(self.server.snapshot(self.data)['view_currency'],'EURO')
        with self.assertRaises(ValueError): self.server.action('/api/goal',{'amount':'0.001'},self.data)

    def test_real_rate_inversion_and_cache(self):
        rows=[dict(base='GHS',quote=code,rate=rate,date='2026-11-17') for code,rate in [('USD',.1),('GBP',.05),('EUR',.08),('XOF',50)]]
        calls=[]
        rates=RateService(live=True,fetcher=lambda params: calls.append(params) or rows)
        self.assertEqual(rates.latest()['rates']['USD'],Decimal(10))
        self.assertEqual(rates.latest()['status'],'reference')
        self.assertEqual(len(calls),1)
        rates.checked=0
        rates.fetcher=lambda _: (_ for _ in ()).throw(OSError('Offline'))
        self.assertEqual(rates.latest()['status'],'stale')
        fresh=RateService(live=True,fetcher=rates.fetcher)
        self.assertEqual(fresh.latest()['status'],'example')

    def test_history_never_fabricates_data_and_validates_pair(self):
        rates=RateService(live=True,fetcher=lambda params:[dict(base='USD',quote='GHS',date='2026-11-16',rate=11.7)])
        self.assertEqual(rates.history('USD','GHS',7)['points'],[{'date':'2026-11-16','rate':11.7}])
        for pair in [('BAD','USD',7),('USD','USD',7),('USD','GHS',999)]:
            with self.assertRaises(ValueError): rates.history(*pair)
        rates.fetcher=lambda _: (_ for _ in ()).throw(OSError('Offline'))
        self.assertEqual(rates.history('USD','GHS',30)['points'],[])
