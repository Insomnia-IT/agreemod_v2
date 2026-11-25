import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from grist_updater.run_updater import main_cycle


class SyncStateRefreshTests(unittest.IsolatedAsyncioTestCase):
    async def test_main_cycle_reloads_sync_state_before_fetching_tables(self):
        events = []

        async def record_init():
            events.append("reload")

        async def record_table(_config):
            events.append("table")

        sync = SimpleNamespace(
            init_sync_state=AsyncMock(side_effect=record_init),
            update_utility_data=AsyncMock(
                side_effect=lambda: events.append("utility")
            ),
            order_tables_by_dependencies=Mock(
                return_value=[{"grist_table": "People"}]
            ),
        )

        with patch(
            "grist_updater.run_updater.sync_table_with_retry",
            side_effect=record_table,
        ), patch(
            "grist_updater.run_updater.sync_directions_with_retry",
            new=AsyncMock(),
        ), patch(
            "grist_updater.run_updater.TABLES_CONFIG",
            [{"grist_table": "People"}],
        ):
            await main_cycle(sync)

        self.assertEqual(events, ["reload", "utility", "table"])


if __name__ == "__main__":
    unittest.main()
