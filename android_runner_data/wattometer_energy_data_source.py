import pandas as pd
import os
import glob
from typing import Optional
from .base_energy_data_source import BaseEnergyDataSource

class WattoMeterEnergyDataSource(BaseEnergyDataSource):
    def __init__(self, source: str, data_source_path: str, name: Optional[str] = None, handle_duplicates: bool = True):
        super().__init__(source, data_source_path, name=name, handle_duplicates=handle_duplicates)

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
        df = pd.read_csv(
            file_path,
            names=["Timestamp", "BusVolts", "CurrentMilliAmps", "PowerWatts"],
            header=0
        )
        # Convert Timestamp text -> unix timestamp (milliseconds)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce").astype('int64') // 10**6
        self._data = df
