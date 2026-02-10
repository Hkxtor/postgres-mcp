from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from postgres_mcp.database_health.sequence_health_calc import SequenceHealthCalc


class TestSequenceHealthCalc:
    @pytest.mark.asyncio
    async def test_get_sequence_metrics_success(self):
        # Mock SQL driver
        mock_driver = MagicMock()
        mock_driver.execute_query = AsyncMock()

        # Mock data returned by the new query
        mock_row = MagicMock()
        mock_row.cells = {
            "schema": "sys",
            "sequence": "queue_id_seq",
            "last_value": 100,
            "max_value": 1000,
            "column_type": "bigint",
            "table_name": "pg_queue",
            "column_name": "qid",
            "readable": True,
        }
        mock_driver.execute_query.return_value = [mock_row]

        calc = SequenceHealthCalc(sql_driver=mock_driver, threshold=0.9)
        metrics = await calc._get_sequence_metrics()  # pyright: ignore[reportPrivateUsage]

        assert len(metrics) == 1
        m = metrics[0]
        assert m.schema == "sys"
        assert m.sequence == "queue_id_seq"
        assert m.table == "pg_queue"
        assert m.column == "qid"
        assert m.last_value == 100
        assert m.max_value == 1000
        assert m.is_healthy is True
        assert m.readable is True

    @pytest.mark.asyncio
    async def test_get_sequence_metrics_none_last_value(self):
        # Mock SQL driver
        mock_driver = MagicMock()
        mock_driver.execute_query = AsyncMock()

        # Mock data with last_value = None (never used)
        mock_row = MagicMock()
        mock_row.cells = {
            "schema": "public",
            "sequence": "test_seq",
            "last_value": None,
            "max_value": 1000,
            "column_type": "integer",
            "table_name": "test_table",
            "column_name": "id",
            "readable": True,
        }
        mock_driver.execute_query.return_value = [mock_row]

        calc = SequenceHealthCalc(sql_driver=mock_driver, threshold=0.9)
        metrics = await calc._get_sequence_metrics()  # pyright: ignore[reportPrivateUsage]

        assert len(metrics) == 1
        assert metrics[0].last_value == 0
        assert metrics[0].is_healthy is True

    @pytest.mark.asyncio
    async def test_get_sequence_metrics_not_readable(self):
        # Mock SQL driver
        mock_driver = MagicMock()
        mock_driver.execute_query = AsyncMock()

        # Mock data with readable = False
        mock_row = MagicMock()
        mock_row.cells = {
            "schema": "secret",
            "sequence": "secret_seq",
            "last_value": None,
            "max_value": 1000,
            "column_type": "integer",
            "table_name": "secret_table",
            "column_name": "id",
            "readable": False,
        }
        mock_driver.execute_query.return_value = [mock_row]

        calc = SequenceHealthCalc(sql_driver=mock_driver, threshold=0.9)
        metrics = await calc._get_sequence_metrics()  # pyright: ignore[reportPrivateUsage]

        # Should skip non-readable sequences
        assert len(metrics) == 0

    @pytest.mark.asyncio
    async def test_get_sequence_metrics_unhealthy(self):
        # Mock SQL driver
        mock_driver = MagicMock()
        mock_driver.execute_query = AsyncMock()

        # Mock data that is unhealthy (95% used > 90% threshold)
        mock_row = MagicMock()
        mock_row.cells = {
            "schema": "public",
            "sequence": "danger_seq",
            "last_value": 950,
            "max_value": 1000,
            "column_type": "integer",
            "table_name": "danger_table",
            "column_name": "id",
            "readable": True,
        }
        mock_driver.execute_query.return_value = [mock_row]

        calc = SequenceHealthCalc(sql_driver=mock_driver, threshold=0.9)
        metrics = await calc._get_sequence_metrics()  # pyright: ignore[reportPrivateUsage]

        assert len(metrics) == 1
        assert metrics[0].is_healthy is False
        assert metrics[0].percent_used == 95.0
