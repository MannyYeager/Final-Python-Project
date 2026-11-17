"""Local wallet simulation with reference-rate quotes and saved demo methods."""
import argparse
import csv
import io
import secrets
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from exchange import RateService
from local_web import LocalServer
from wallet import Wallet, currency_code, money, positive_amount


def initial_session():
    return {'wallet': Wallet('Your wallet'), 'history': [], 'view_currency': 'GHS', 'goal': '1000.00',
            'methods': [{'id': 'card-demo', 'type': 'card', 'label': 'Everyday demo card', 'suffix': '4242'},
                        {'id': 'bank-demo', 'type': 'bank', 'label': 'Demo savings account', 'suffix': '1208'},
                        {'id': 'mobile-demo', 'type': 'mobile', 'label': 'Demo mobile money', 'suffix': '0550'}],
            'pending_quote': None, 'completed_quotes': []}


class WalletServer(LocalServer):
    read_paths = {'/api/market'}

    def __init__(self, address, rate_service=None):
        super().__init__(address, Path(__file__).with_name('static'), 'wallet_lab_session', initial_session)
        self.rate_service = rate_service or RateService()

    def snapshot(self, data):
        reference = self.rate_service.latest()
        wallet = data['wallet']
        wallet.rates = dict(reference['rates'])
        quote = data.get('pending_quote')
        return {'balance': str(wallet.balance), 'name': wallet.user, 'simulation': True,
                'currencies': [{'code': code, 'rate': str(rate), 'balance': str(money(wallet.balance / rate)),
                                'date': reference['dates'].get(code, '')} for code, rate in wallet.rates.items()],
                'rate_info': {k: v for k, v in reference.items() if k != 'rates'},
                'history': list(reversed(data['history'])), 'methods': data['methods'],
                'view_currency': data['view_currency'], 'goal': data['goal'],
                'pending_quote': quote if quote and quote['expires'] > time.time() else None}

    def read(self, path, query, data):
        try:
            days = int(query.get('days', ['30'])[0])
        except ValueError:
            raise ValueError('Choose a valid date range.') from None
        return self.rate_service.history(currency_code(query.get('base', ['USD'])[0]),
                                         currency_code(query.get('quote', ['GHS'])[0]), days)

    def make_quote(self, payload, data):
        kind, currency = payload.get('kind'), payload.get('currency', '')
        if not isinstance(kind, str) or kind not in {'deposit', 'withdraw', 'withdraw_all'} or not isinstance(currency, str):
            raise ValueError('Choose a transaction and currency.')
        reference = self.rate_service.latest()
        code = currency_code(currency)
        if code not in reference['rates']:
            raise ValueError('Choose a supported currency.')
        method_id = payload.get('method_id', 'card-demo' if kind == 'deposit' else 'bank-demo')
        method = next((m for m in data['methods'] if m['id'] == method_id), None)
        if not method:
            raise ValueError('Choose an available saved payment method.')
        note = payload.get('note', '')
        if not isinstance(note, str) or len(note) > 140:
            raise ValueError('Keep the transaction note under 140 characters.')
        raw = payload.get('amount', '')
        if isinstance(raw, bool) or not isinstance(raw, (str, int, float)):
            raise ValueError('Enter a numeric amount.')
        rate = reference['rates'][code]
        amount = money(data['wallet'].balance / rate) if kind == 'withdraw_all' else positive_amount(raw)
        if amount <= 0:
            raise ValueError('No balance available in this currency.')
        ghs = data['wallet'].balance if kind == 'withdraw_all' else money(amount * rate)
        if ghs <= 0:
            raise ValueError('Amount is too small after conversion.')
        if kind != 'deposit' and ghs > data['wallet'].balance:
            raise ValueError('Insufficient Balance')
        return {'id': secrets.token_hex(8), 'kind': kind, 'currency': code, 'amount': str(amount),
                'ghs': str(ghs), 'fee': '0.00', 'rate': str(rate), 'rate_date': reference['dates'].get(code, ''),
                'source': reference['source'], 'rate_status': reference['status'], 'method': dict(method),
                'note': note.strip(), 'balance_before': str(data['wallet'].balance), 'expires': time.time() + 120}

    def action(self, path, payload, data):
        if path == '/api/preferences':
            code = currency_code(payload.get('view_currency', ''))
            if code not in self.rate_service.latest()['rates']:
                raise ValueError('Choose a supported display currency.')
            data['view_currency'] = code
            return 'Balance display currency updated.'
        if path == '/api/goal':
            target = money(positive_amount(payload.get('amount')))
            if target <= 0:
                raise ValueError('Use a savings target of at least GHS 0.01.')
            data['goal'] = str(target)
            return 'Savings target updated.'
        if path == '/api/method':
            kind, label, suffix = payload.get('type'), payload.get('label'), payload.get('suffix')
            if not isinstance(kind, str) or kind not in {'card', 'bank', 'mobile'} or not isinstance(label, str) or not 1 <= len(label.strip()) <= 50:
                raise ValueError('Choose a method type and a label of up to 50 characters.')
            if not isinstance(suffix, str) or len(suffix) != 4 or not suffix.isascii() or not suffix.isdigit():
                raise ValueError('Use four example ending digits, not a full account or card number.')
            if len(data['methods']) >= 8:
                raise ValueError('You can save up to eight demo methods.')
            data['methods'].append({'id': secrets.token_hex(6), 'type': kind, 'label': label.strip(), 'suffix': suffix})
            return 'Demo payment method saved.'
        if path == '/api/method/delete':
            methods = [m for m in data['methods'] if m['id'] != payload.get('id')]
            if len(methods) == len(data['methods']):
                raise ValueError('Payment method not found.')
            data['methods'] = methods
            data['pending_quote'] = None
            return 'Demo method removed.'
        if path == '/api/quote':
            data['pending_quote'] = self.make_quote(payload, data)
            return 'Review your transaction. This quote is valid for two minutes.'
        if path != '/api/transaction':
            raise ValueError('Unknown wallet action.')
        quote_id = payload.get('quote_id')
        if quote_id:
            if quote_id in data['completed_quotes']:
                return 'This transaction has already completed.'
            quote = data.get('pending_quote')
            if not quote or quote['id'] != quote_id or quote['expires'] <= time.time():
                raise ValueError('This quote expired. Review a new transaction.')
            if not any(m['id'] == quote['method']['id'] for m in data['methods']):
                raise ValueError('This payment method is no longer available.')
            if data['wallet'].balance != Decimal(quote['balance_before']):
                raise ValueError('Your balance changed. Review this transaction again.')
        else:
            quote = self.make_quote(payload, data)
        wallet = data['wallet']
        before = wallet.balance
        wallet.rates[quote['currency']] = Decimal(quote['rate'])
        result = (wallet.withdraw_all(quote['currency']) if quote['kind'] == 'withdraw_all' else
                  wallet.deposit(quote['amount'], quote['currency']) if quote['kind'] == 'deposit' else
                  wallet.withdrawal(quote['amount'], quote['currency']))
        if wallet.balance == before:
            raise ValueError(result)
        delta = wallet.balance - before
        data['history'].append({**quote, 'reference': 'CD-' + secrets.token_hex(4).upper(),
                                'ghs': str(abs(delta)), 'balance': str(wallet.balance),
                                'time': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')})
        data['completed_quotes'].append(quote['id'])
        data['pending_quote'] = None
        return f"{'Deposit added' if delta > 0 else 'Withdrawal completed'}. Your simulated balance is GHS {wallet.balance:.2f}."

    def export(self, data):
        buffer = io.StringIO(newline='')
        writer = csv.writer(buffer)
        writer.writerow(['Reference', 'Date', 'Type', 'Currency', 'Amount', 'GHS change', 'Balance GHS', 'Method', 'Note'])
        for row in data['history']:
            safe = lambda value: "'" + value if value.startswith(('=', '+', '-', '@')) else value
            writer.writerow([row['reference'], row['time'], row['kind'], row['currency'], row['amount'], row['ghs'],
                             row['balance'], safe(row['method']['label']), safe(row['note'])])
        return buffer.getvalue(), 'cedi-activity.csv'


def main():
    parser = argparse.ArgumentParser(description='Cedi wallet local simulation')
    parser.add_argument('--port', type=int, default=8766)
    parser.add_argument('--offline', action='store_true', help='Use labelled teaching rates without external requests')
    args = parser.parse_args()
    rates = RateService(live=not args.offline)
    rates.latest()
    with WalletServer(('127.0.0.1', args.port), rates) as server:
        print(f'Wallet preview: http://127.0.0.1:{server.server_port}/', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
