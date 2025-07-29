import pandas as pd
import os
import glob
from typing import Optional
from .base_energy_data_source import BaseEnergyDataSource

class BatteryManagerEnergyDataSource(BaseEnergyDataSource):
    def __init__(self, source: str, data_source_path: str, name: Optional[str] = None, handle_duplicates: bool = True, duplicate_tolerance_percent: float = 5.0):
        super().__init__(source, data_source_path, name=name, handle_duplicates=handle_duplicates, duplicate_tolerance_percent=duplicate_tolerance_percent)

    def _load_data_impl(self):
        # Detect the CSV file if data_source_path is a directory
        if os.path.isdir(self.data_source_path):
            csv_files = glob.glob(os.path.join(self.data_source_path, "*.csv"))
            if not csv_files:
                raise FileNotFoundError(f"No CSV file found in {self.data_source_path}")
            file_path = csv_files[0]
        else:
            file_path = self.data_source_path
        self.data_file_name = os.path.basename(file_path)
        df = pd.read_csv(file_path)
        # Convert required columns
        df["CurrentMilliAmps"] = pd.to_numeric(df["BATTERY_PROPERTY_CURRENT_NOW"], errors="coerce") / 1000.0  # µA -> mA
        df["BusVolts"] = pd.to_numeric(df["EXTRA_VOLTAGE"], errors="coerce") / 1000.0  # mV -> V
        # Compute power in Watts
        df["PowerWatts"] = df["BusVolts"] * (df["CurrentMilliAmps"] / 1000.0)  # mA -> A
        # Build the standard DataFrame
        self._data = df.rename(columns={"Timestamp": "Timestamp"})[
            ["Timestamp", "BusVolts", "CurrentMilliAmps", "PowerWatts"]
        ]
