"""Cached Frankfurter reference rates. Never invent historical observations."""
import json
import time
import sys
from datetime import date, timedelta
from decimal import Decimal
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from wallet import RATES

API = 'https://api.frankfurter.dev/v2/rates'
CODES = {'GHS': 'GHS', 'USD': 'USD', 'GBP': 'GBP', 'EURO': 'EUR', 'CFA': 'XOF'}


class RateService:
    def __init__(self, live=False, fetcher=None):
        self.live = live
        self.fetcher = fetcher or self._fetch
        self.cached = None
        self.checked = 0
        self.series = {}

    @staticmethod
    def _fetch(params):
        request = Request(API + '?' + urlencode(params), headers={'User-Agent': 'CediPortfolio/2.0', 'Accept': 'application/json'})
        for attempt in range(2):
            try:
                with urlopen(request, timeout=10) as response:
                    raw = response.read(500001)
                break
            except OSError:
                if attempt:
                    raise
        if len(raw) > 500000:
            raise ValueError('Rate response too large.')
        return json.loads(raw)

    def latest(self):
        if not self.live:
            return {'rates': dict(RATES), 'status': 'example', 'source': 'Offline teaching rates', 'dates': {}, 'error': ''}
        if time.time() - self.checked < 900 and self.cached:
            return self.cached
        self.checked = time.time()
        try:
            rows = self.fetcher({'base': 'GHS', 'quotes': 'USD,GBP,EUR,XOF'})
            rates, dates = {'GHS': Decimal(1)}, {}
            for internal, code in CODES.items():
                if code == 'GHS':
                    continue
                row = next(r for r in rows if r['base'] == 'GHS' and r['quote'] == code)
                rate = Decimal(str(row['rate']))
                if not rate.is_finite() or not Decimal('0.000000000001') <= rate <= Decimal('1000000000000'):
                    raise ValueError('Invalid reference rate.')
                date.fromisoformat(row['date'])
                rates[internal], dates[internal] = Decimal(1) / rate, row['date']
            self.cached = {'rates': rates, 'status': 'reference', 'source': 'Frankfurter · blended reference rates', 'dates': dates, 'error': ''}
        except (OSError, ValueError, KeyError, TypeError, StopIteration, ArithmeticError):
            if self.cached and self.cached['status'] in {'reference', 'stale'}:
                self.cached = {**self.cached, 'status': 'stale', 'error': 'Rate service unavailable. Showing the last retrieved reference rates.'}
            else:
                self.cached = {'rates': dict(RATES), 'status': 'example', 'source': 'Offline teaching rates', 'dates': {},
                               'error': 'Reference rates unavailable. Transactions use clearly labelled example rates until the service recovers.'}
        return self.cached

    def history(self, base, quote, days):
        if base not in CODES or quote not in CODES or base == quote or days not in {7, 30, 90}:
            raise ValueError('Choose different supported currencies and a 7, 30 or 90 day range.')
        key = (base, quote, days)
        if key in self.series and time.time() - self.series[key][0] < 3600:
            return self.series[key][1]
        result = {'base': base, 'quote': quote, 'days': days, 'points': [], 'source': 'Frankfurter', 'error': ''}
        if not self.live:
            return {**result, 'error': 'Historical reference data needs an internet connection.'}
        try:
            rows = self.fetcher({'base': CODES[base], 'quotes': CODES[quote],
                                 'from': (date.today() - timedelta(days=days)).isoformat(), 'to': date.today().isoformat()})
            points = {}
            for row in rows:
                if row['base'] != CODES[base] or row['quote'] != CODES[quote]:
                    continue
                day = date.fromisoformat(row['date']).isoformat()
                value = Decimal(str(row['rate']))
                if not value.is_finite() or not Decimal('0.000000000001') <= value <= Decimal('1000000000000'):
                    raise ValueError('Invalid historical rate.')
                points[day] = float(value)
            result['points'] = [{'date': day, 'rate': points[day]} for day in sorted(points)]
            if not result['points']:
                result['error'] = 'No observations were published for this pair and date range.'
            self.series[key] = (time.time(), result)
        except (OSError, ValueError, KeyError, TypeError, ArithmeticError) as error:
            print(f'Rate history unavailable ({type(error).__name__}): {error}', file=sys.stderr, flush=True)
            result['error'] = 'Historical rates could not be loaded. Retry when the rate service is available.'
        return result
