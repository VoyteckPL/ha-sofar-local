from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    BLOCKS,
    CONF_LOGGER_SERIAL,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)
from .protocol import parse_block, read_register_block

_LOGGER = logging.getLogger(__name__)

OFFLINE_INTERVAL = timedelta(seconds=60)


class SofarCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self.logger_serial = entry.data[CONF_LOGGER_SERIAL]
        self.is_online = True
        self._consecutive_failed_cycles = 0
        self._online_interval = timedelta(
            seconds=int(
                entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            )
        )

        super().__init__(
            hass,
            _LOGGER,
            name="Sofar Local",
            update_interval=self._online_interval,
        )

    async def _read_block(self, start: int, end: int):
        last_err = None
        for attempt in range(2):
            try:
                raw = await read_register_block(
                    self.host,
                    self.port,
                    self.logger_serial,
                    start,
                    end,
                )
                return parse_block(start, raw)
            except Exception as err:
                last_err = err
                if attempt == 0:
                    await asyncio.sleep(1.0)

        _LOGGER.debug(
            "SOFAR block 0x%04X failed: %s: %r",
            start,
            type(last_err).__name__,
            last_err,
        )
        return None

    async def _async_update_data(self) -> dict:
        result = dict(self.data or {})
        successful_blocks = 0

        for index, (start, end) in enumerate(BLOCKS):
            block_data = await self._read_block(start, end)

            if block_data is not None:
                result.update(block_data)
                successful_blocks += 1
            elif successful_blocks == 0 and index >= 1:
                # Falownik/logger nie odpowiada (np. noc) - nie męcz reszty bloków.
                break

            if index < len(BLOCKS) - 1:
                await asyncio.sleep(1.0)

        if successful_blocks > 0:
            if not self.is_online:
                _LOGGER.info("SOFAR inverter is back online")
            self._consecutive_failed_cycles = 0
            self.is_online = True
            self.update_interval = self._online_interval
        else:
            self._consecutive_failed_cycles += 1

            if self._consecutive_failed_cycles >= 2:
                if self.is_online:
                    _LOGGER.warning(
                        "SOFAR inverter at %s:%s not responding, assuming offline "
                        "(night?); polling every %d s until it returns",
                        self.host,
                        self.port,
                        int(OFFLINE_INTERVAL.total_seconds()),
                    )
                self.is_online = False
                result["current_power"] = 0
                self.update_interval = OFFLINE_INTERVAL

        return result
