"""Read-only queries must follow the current connection and retain its snapshot contract."""
from unittest.mock import Mock

import pytest

from eija_studio.application.repository import RepositorySource
from eija_studio.domain.models import DomainError


@pytest.mark.parametrize(("query", "operation", "args", "port_args"), [
    ("repository_impact", "impact", ("approval",), ("approval",)),
    ("repository_source", "read_source", ("repo://src/approval.py#approve",), ("repo://src/approval.py#approve",)),
    ("repository_freshness", "freshness", (), ()),
])
def test_query_observes_replaced_and_removed_connection_without_store_access(studio, monkeypatch,
                                                                          query, operation, args, port_args):
    def forbidden_transaction():
        raise AssertionError("A repository query must not enter the change-case store")

    monkeypatch.setattr(studio.store, "transaction", forbidden_transaction)
    expected = "sha256:" + "1" * 64
    read = getattr(studio, query)
    unconfigured = {"status": "unconfigured", "reason": "Start with --repo PATH to inspect a local repository"}
    studio.repository = None
    assert read(*args, expected_source_hash=expected) == unconfigured

    first, second = Mock(spec=RepositorySource), Mock(spec=RepositorySource)
    for connection in (first, second):
        studio.repository = connection
        payload = {"source_hash": expected, "complete": False}
        operation_mock = getattr(connection, operation)
        operation_mock.return_value = payload
        assert read(*args, expected_source_hash=expected) is payload
        operation_mock.assert_called_once_with(*port_args, expected_source_hash=expected)
    getattr(first, operation).assert_called_once()

    refused = DomainError("SOURCE_SNAPSHOT_STALE", "The captured snapshot is stale", {"expected_source_hash": expected})
    getattr(second, operation).side_effect = refused
    with pytest.raises(DomainError) as caught:
        read(*args, expected_source_hash=expected)
    assert caught.value is refused

    studio.repository = None
    assert read(*args, expected_source_hash=expected) == unconfigured
    assert getattr(second, operation).call_count == 2
