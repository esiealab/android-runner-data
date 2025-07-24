# Init file for src package

import logging

logger = logging.getLogger("android_runner_data")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

from .batterymanager_energy_data_source import BatteryManagerEnergyDataSource
from .wattometer_energy_data_source import WattoMeterEnergyDataSource
from .base_energy_data_source import BaseEnergyDataSource

SOURCE_CLASS_MAP = {
    "batterymanager": BatteryManagerEnergyDataSource,
    "wattometer": WattoMeterEnergyDataSource
}
