import pytest
import base58

from ledger.compact_merkle_tree import CompactMerkleTree
from ledger.ledger import Ledger
from plenum.common.constants import TXN_TYPE, TARGET_NYM, DATA, NAME, ALIAS, SERVICES, VALIDATOR, IDENTIFIER, NODE_PORT, CLIENT_PORT, NODE_IP
from plenum.common.stack_manager import TxnStackManager
from json.decoder import JSONDecodeError
import logging


whitelist = ['substring not found']


@pytest.fixture(scope="function")
def invalid_verkey_tdir(tdir_for_func):
    tree = CompactMerkleTree()
    ledger = Ledger(CompactMerkleTree(), dataDir=tdir_for_func)
    for d in range(3):
        txn = {TXN_TYPE: '0',
               TARGET_NYM: base58.b58encode(b'whatever'),
               IDENTIFIER: "Th7MpTaRZVRYnPiabds81Y",
               DATA: {
                   NAME: str(d),
                   ALIAS: 'test' + str(d),
                   SERVICES: [VALIDATOR],
               }
               }
        if d == 1:
            txn[TARGET_NYM] = "invalid===="
        ledger.add(txn)
    return ledger


@pytest.fixture(scope="function")
def invalid_identifier_tdir(tdir_for_func):
    tree = CompactMerkleTree()
    ledger = Ledger(CompactMerkleTree(), dataDir=tdir_for_func)
    txn = {TXN_TYPE: '0',
           TARGET_NYM: base58.b58encode(b'whatever'),
           IDENTIFIER: "invalid====",
           DATA: {
                NAME: str(2),
                ALIAS: 'test' + str(2),
                SERVICES: [VALIDATOR],
           }
           }
    ledger.add(txn)
    return ledger


class DummyLedger(Ledger):
    def getAllTxn(self, frm: int=None, to: int=None):
        raise JSONDecodeError('', '', 0)

                                                            
def test_parse_verkey_non_base58_txn_type_field_raises_SystemExit_has_descriptive_error(invalid_verkey_tdir, tdir_for_func):
    """
    Test that invalid base58 TARGET_NYM in pool_transaction raises the proper exception (INDY-150)
    """
    with pytest.raises(SystemExit) as excinfo:
        ledger = Ledger(CompactMerkleTree(), dataDir=tdir_for_func)
        _, _, nodeKeys = TxnStackManager.parseLedgerForHaAndKeys(ledger)
    assert excinfo.value.code == 'Invalid verkey. Rebuild pool transactions.'
    ledger.stop()


def test_parse_identifier_non_base58_txn_type_field_raises_SystemExit_has_descriptive_error(invalid_identifier_tdir, tdir_for_func):
    """
    Test that invalid base58 IDENTIFIER in pool_transaction raises the proper exception (INDY-150)
    """
    with pytest.raises(SystemExit) as excinfo:
        ledger = Ledger(CompactMerkleTree(), dataDir=tdir_for_func)
        _, _, nodeKeys = TxnStackManager.parseLedgerForHaAndKeys(ledger)
    assert excinfo.value.code == 'Invalid identifier. Rebuild pool transactions.'
    ledger.stop()


def test_pool_file_is_invalid_raises_SystemExit_has_descriptive_error(tdir_for_func):
    """
    Test that that invalid pool_transaction file raises the proper exception (INDY-150)
    """
    ledger = DummyLedger(CompactMerkleTree(), dataDir=tdir_for_func)
    with pytest.raises(SystemExit) as excinfo:
        _, _, nodeKeys = TxnStackManager.parseLedgerForHaAndKeys(ledger)
    assert excinfo.value.code == 'Pool transaction file corrupted. Rebuild pool transactions.'
    ledger.stop()
