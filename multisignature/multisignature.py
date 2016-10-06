#!/usr/bin/python
""" A multisignature library designed for demonstration of multisignature concepts

"""

import click, requests

from bitcoin import *
from termcolor import colored
from tabulate import tabulate

class MultiSignature(object):

    def generate_address(self):

        private_key_one = self.generate_private_key()
        private_key_two = self.generate_private_key()
        private_key_three = self.generate_private_key()

        print colored("Generate private keys:", "yellow")
        print "\t1 - ", private_key_one
        print "\t2 - ", private_key_two
        print "\t3 - ", private_key_three        

        public_key_one = self.get_public_key(private_key_one)
        public_key_two = self.get_public_key(private_key_two)
        public_key_three = self.get_public_key(private_key_three)

        print colored("Generated public keys:", "yellow")
        print "\t1 - ", self.get_public_address(public_key_one)
        print "\t2 - ", self.get_public_address(public_key_two)
        print "\t3 - ", self.get_public_address(public_key_three)

        redeem_script = self.create_redeem_script([public_key_one, public_key_two, public_key_three])

        print colored("Redeem script:", "yellow")
        print "\t", redeem_script

        multisignature_address = self.redeem_script_to_address(redeem_script)

        print colored("Multisignature address:", "yellow")
        print "\t", multisignature_address


    def get_unspents(self, address):

        table = []

        # Make a request to the BitGo API to retrieve all unspent Bitcoin associated
        # with the provided address
        response = requests.get('https://www.bitgo.com/api/v1/address/' + address + '/tx')

        transactions = response.json()['transactions']

        # Retrieve the necessary information from the transaction payload
        for transaction in transactions:
          date = transaction['date']
          unspents = transaction['outputs']
          transaction_id = transaction['id']
          for unspent in unspents:
              table.append([date, transaction_id, unspent['account'], unspent['value'], unspent['vout']])

        print tabulate(table, headers=["Date", "Transaction ID", "Address", "Value", "Vout"])


    def create_raw_transaction(self, txid, vout, address, amount, change_address, fee):
        raw_transaction =  self._create_raw_transaction(txid, vout, address, amount, change_address, fee)

        print colored("Raw transaction:", "yellow")
        print raw_transaction


    def sign_transaction(self, private_key, transaction):
        index = 0
        signed_transaction = self._sign_transaction(transaction, index, private_key)
        print colored("Signed transaction:", "yellow")
        print signed_transaction


    # Address creation methods

    @staticmethod
    def generate_private_key():
        return sha256(str(random.randrange(2**256)))


    @staticmethod
    def get_public_key(private_key):
        return privtopub(private_key)


    @staticmethod
    def get_public_address(public_key):
        return pubtoaddr(public_key)


    @staticmethod
    def create_redeem_script(public_keys):
        return mk_multisig_script(public_keys, 2, 3)


    @staticmethod
    def redeem_script_to_address(redeem_script):
        return p2sh_scriptaddr(redeem_script)


    # Transaction creation and signing methods

    @staticmethod
    def _create_raw_transaction(transaction_id, vout, address, amount, change_address, fee):
        inputs = [transaction_id + ':' + vout]
        outputs = [address + ':' + amount]
        return mktx(inputs, outputs, change_address, fee)


    @staticmethod
    def _sign_transaction(transaction, index, private_key):
        return sign(transaction, index, private_key)


@click.group(help='')
def cli():
    pass


@click.command('generate_address')
def generate_address():
    MultiSignature().generate_address()


@click.command('get_unspent')
@click.option('--address', help='Bitcoin address', required=True)
def get_unspents(address):
    MultiSignature().get_unspents(address)


@click.command('create_raw_transaction')
@click.option('--txid', help='Transaction Id', required=True)
@click.option('--vout', help='The vout or index of the unspent', required=True)
@click.option('--address', help='The recipients address', required=True)
@click.option('--amount', help='The amount to send', required=True)
def create_raw_transaction(txid, vout, address, amount):
    MultiSignature().create_raw_transaction(txid, vout, address, amount)


@click.command('sign_transaction')
@click.option('--private_key', help='Private key', required=True)
@click.option('--transaction', help='Transaction', required=True)
def sign_transaction(private_key, transaction):
    MultiSignature().sign_transaction(private_key, transaction)


cli.add_command(generate_address)
cli.add_command(get_unspents)
cli.add_command(create_raw_transaction)
cli.add_command(sign_transaction)


if __name__ == '__main__':
    cli()

