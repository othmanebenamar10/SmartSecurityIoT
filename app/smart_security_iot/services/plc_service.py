from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from smart_security_iot.core.config import AppConfig


@dataclass
class PlcState:
    connected: bool = False
    light_on: bool = False
    light_timer_start: float = 0.0


class PlcService:
    def __init__(self, config: AppConfig, logger: logging.Logger) -> None:
        self._config = config
        self._logger = logger
        self._state = PlcState()
        self._modbus = None

    def connect(self) -> bool:
        if self._state.connected:
            return True
        try:
            from pymodbus.client import ModbusTcpClient

            client = ModbusTcpClient(self._config.plc_ip, port=self._config.plc_port, timeout=1.0)
            result = client.connect()
            if result:
                self._modbus = client
                self._state.connected = True
                self._logger.info("PLC connected to %s:%d", self._config.plc_ip, self._config.plc_port)
                return True
            client.close()
            self._logger.warning("PLC connection failed to %s:%d", self._config.plc_ip, self._config.plc_port)
            return False
        except Exception as ex:
            self._logger.warning("PLC connection error: %s", ex)
            return False

    def disconnect(self) -> None:
        if self._modbus is not None:
            try:
                self._modbus.close()
            except Exception:
                pass
            self._modbus = None
        self._state.connected = False
        self._state.light_on = False

    def set_light(self, on: bool) -> bool:
        coil = self._config.plc_light_coil
        try:
            if self._modbus is not None and self._state.connected:
                self._modbus.write_coil(coil, on)
                self._logger.info("PLC light coil %d set to %s", coil, on)
            else:
                self._logger.info("PLC not connected - virtual light %s", "ON" if on else "OFF")
        except Exception as ex:
            self._logger.warning("PLC write_coil error: %s", ex)
            if not self._state.connected:
                self._logger.info("Virtual light %s (PLC unavailable)", "ON" if on else "OFF")
        self._state.light_on = on
        if on:
            self._state.light_timer_start = time.time()
        return True

    def check_light_timer(self) -> bool:
        if self._state.light_on and self._state.light_timer_start > 0:
            elapsed = time.time() - self._state.light_timer_start
            if elapsed >= self._config.light_on_seconds:
                self.set_light(False)
                self._logger.info("Light auto-off after %ds", self._config.light_on_seconds)
                return False
        return self._state.light_on

    @property
    def is_connected(self) -> bool:
        return self._state.connected

    @property
    def is_light_on(self) -> bool:
        return self._state.light_on

    @property
    def light_remaining(self) -> float:
        if not self._state.light_on or self._state.light_timer_start == 0:
            return 0.0
        elapsed = time.time() - self._state.light_timer_start
        remaining = self._config.light_on_seconds - elapsed
        return max(0.0, remaining)
