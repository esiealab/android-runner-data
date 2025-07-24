from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd
import numpy as np
from android_runner_data import logger

class BaseEnergyDataSource(ABC):
    STANDARD_COLUMNS = ["Timestamp", "BusVolts", "CurrentMilliAmps", "PowerWatts"]

    def __init__(self, source: str, data_source_path: str, name: Optional[str] = None):
        self.source = source
        self.data_source_path = data_source_path  # Can be a folder or a file, handled in load_data
        self.data_file_name = None  # Will be set in load_data
        self._data: Optional[pd.DataFrame] = None
        self._energy_wh = None
        self._power_avg = None
        self._power_std = None
        self._power_min = None
        self._power_max = None
        self._name = name
        self._duration_seconds = None
        self._start_time = None

    @property
    def duration_seconds(self) -> Optional[float]:
        """Returns the duration of the experiment in seconds."""
        return self._duration_seconds

    @property
    def start_time(self) -> Optional[str]:
        """Returns the start time of the experiment as ISO string."""
        return self._start_time

    @property
    def power_avg(self) -> Optional[float]:
        return self._power_avg
    
    @property
    def power_std(self) -> Optional[float]:
        return self._power_std

    @property
    def power_min(self) -> Optional[float]:
        return self._power_min

    @property
    def power_max(self) -> Optional[float]:
        return self._power_max
        # No direct storage for energy in joules, always converted on the fly

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def energy_wh(self) -> Optional[float]:
        return self._energy_wh

    @property
    def energy_joules(self) -> Optional[float]:
        if self._energy_wh is None:
            return None
        return self._energy_wh * 3600.0

    @property
    def data(self):
        return self._data
    
    @abstractmethod
    def _load_data_impl(self):
        """
        To be implemented in subclasses: loads data into self._data and sets self.data_file_name.
        self._data MUST be a pandas DataFrame with the following standard columns:
            - "Timestamp": timestamp (int, in milliseconds since epoch)
            - "BusVolts": bus voltage (float, in volts)
            - "CurrentMilliAmps": current in milliamps (float)
            - "PowerWatts": power in watts (float)
        """
        pass
    
    def load_data(self):
        """
        Loads temporal consumption data into self._data (DataFrame) via the subclass-specific method.
        Then calls extract_experiment_date to set the date, and computes aggregate values.
        Also computes experiment duration and start time from timestamps.
        """
        self._load_data_impl()
        self._energy_wh = self._compute_energy_wh()
        self._power_avg = self._compute_power_average()
        self._power_std = self._compute_power_std()
        self._power_min = self._compute_power_min()
        self._power_max = self._compute_power_max()
        self._start_time = self._compute_start_time()
        self._duration_seconds = self._compute_duration_seconds()
    
    def _compute_start_time(self) -> Optional[str]:
        """
        Computes and returns the start time of the experiment as a short date and time string (YYYY-MM-DD HH:MM:SS).
        """
        if self._data is None or self._data.empty or "Timestamp" not in self._data.columns:
            return None
        timestamps = pd.to_datetime(self._data["Timestamp"], unit="ms", errors="coerce")
        valid_ts = timestamps.dropna()
        if valid_ts.empty:
            return None
        start = valid_ts.iloc[0]
        return start.strftime("%Y-%m-%d %H:%M:%S") if pd.notnull(start) else None

    def _compute_duration_seconds(self) -> Optional[float]:
        """
        Computes and returns the duration (in seconds) of the experiment from the first and last valid timestamps.
        """
        if self._data is None or self._data.empty or "Timestamp" not in self._data.columns:
            return None
        timestamps = pd.to_datetime(self._data["Timestamp"], unit="ms", errors="coerce")
        valid_ts = timestamps.dropna()
        if valid_ts.empty:
            return None
        start = valid_ts.iloc[0]
        end = valid_ts.iloc[-1]
        if pd.notnull(start) and pd.notnull(end):
            return (end - start).total_seconds()
        else:
            return None

    def _compute_power_average(self) -> Optional[float]:
        """
        Computes the average power (in Watts) from the PowerWatts column.
        Returns None if data is missing or incomplete.
        """
        if self._data is None or self._data.empty:
            return None
        power = pd.to_numeric(self._data["PowerWatts"], errors="coerce")
        if power.isnull().any():
            return None
        return float(power.mean())

    def _compute_power_std(self) -> Optional[float]:
        """
        Computes the standard deviation of the power (in Watts) from the PowerWatts column.
        Returns None if data is missing or incomplete.
        """
        if self._data is None or self._data.empty:
            return None
        power = pd.to_numeric(self._data["PowerWatts"], errors="coerce")
        if power.isnull().any():
            return None
        return float(power.std())

    def _compute_power_min(self) -> Optional[float]:
        """
        Computes the minimum power (in Watts) from the PowerWatts column.
        Returns None if data is missing or incomplete.
        """
        if self._data is None or self._data.empty:
            return None
        power = pd.to_numeric(self._data["PowerWatts"], errors="coerce")
        if power.isnull().any():
            return None
        return float(power.min())

    def _compute_power_max(self) -> Optional[float]:
        """
        Computes the maximum power (in Watts) from the PowerWatts column.
        Returns None if data is missing or incomplete.
        """
        if self._data is None or self._data.empty:
            return None
        power = pd.to_numeric(self._data["PowerWatts"], errors="coerce")
        if power.isnull().any():
            return None
        return float(power.max())
    
    def _compute_energy_wh(self) -> Optional[float]:
        """
        Computes the consumed energy (in Wh) from the PowerWatts column
        using the trapezoidal rule on the time series.
        Returns None if data is missing or incomplete.
        Timestamps are converted to milliseconds.
        """
        if self._data is None or self._data.empty:
            return None
        df = self._data
        # Check for required columns
        if not all(col in df.columns for col in self.STANDARD_COLUMNS):
            return None
        # Convert timestamp to milliseconds
        try:
            timestamps = pd.to_datetime(df["Timestamp"], unit="ms", errors="coerce")
            if timestamps.isnull().all():
                timestamps = pd.to_numeric(df["Timestamp"], errors="coerce")
                if timestamps.isnull().any():
                    return None
                # Assume timestamps are already in ms if numeric
                time_ms = timestamps.values
            else:
                # Convert to milliseconds since epoch
                time_ms = timestamps.astype('int64') // 1_000_000  # nanoseconds -> ms
        except Exception:
            return None
        power = pd.to_numeric(df["PowerWatts"], errors="coerce")
        if power.isnull().any():
            return None
        # Compute energy in Wh (Watt * millisecond -> /3_600_000)
        energy_wms = np.trapezoid(power.to_numpy(), np.asarray(time_ms))
        energy_wh = float(energy_wms) / 3_600_000.0
        return energy_wh

    def _compute_energy_joules(self) -> Optional[float]:
        """
        Computes the consumed energy (in Joules) from the PowerWatts column
        using compute_energy_wh (1 Wh = 3600 Joules).
        Returns None if data is missing or incomplete.
        """
        energy_wh = self._compute_energy_wh()
        if energy_wh is None:
            return None
        return energy_wh * 3600.0

    @staticmethod
    def create_from_type(source_type: str, data_source_path: str, name: Optional[str] = None, source_class_map=None):
        """
        Dynamically creates an instance of the correct class from the source type and mapping.
        """
        if source_class_map is None:
            try:
                from android_runner_data import SOURCE_CLASS_MAP
            except ImportError:
                logger.error("Could not import SOURCE_CLASS_MAP")
                raise ValueError("Could not import SOURCE_CLASS_MAP")
        else:
            SOURCE_CLASS_MAP = source_class_map
        cls = SOURCE_CLASS_MAP.get(source_type)
        if cls is None:
            logger.error(f"Unknown source type: {source_type}")
            raise ValueError(f"Unknown source type: {source_type}")
        logger.debug(f"Creating instance {cls.__name__} for {data_source_path} (name={name})")
        return cls(source=source_type, data_source_path=data_source_path, name=name)

    @staticmethod
    def load_experiments(experiments):
        """
        Takes a list of experiment dicts (with data_path and optionally data_path_global) and returns a list of BaseEnergyDataSource instances.
        """
        import os
        sources = []
        for exp in experiments:
            source_type = exp["source_type"]
            data_path = exp["data_path"]
            data_path_global = exp.get("data_path_global")
            name = exp.get("name")
            if data_path_global:
                logger.info(f"Searching subfolders in {data_path_global} for {source_type}")
                for subdir in os.listdir(data_path_global):
                    if subdir.startswith('.'):
                        continue
                    subdir_path = os.path.join(data_path_global, subdir)
                    if os.path.isdir(subdir_path):
                        full_data_path = os.path.join(subdir_path, data_path)
                        logger.info(f"Loading data for {source_type} from {full_data_path}")
                        try:
                            obj = BaseEnergyDataSource.create_from_type(source_type, full_data_path, name=name)
                            obj.load_data()
                            sources.append(obj)
                        except ValueError as e:
                            logger.error(f"Error loading data for {source_type} from {full_data_path}: {e}")
                            continue
                        except FileNotFoundError as e:
                            logger.error(f"File not found for {source_type} at {data_path}: {e}")
                            continue
            else:
                logger.info(f"Loading data for {source_type} from {data_path}")
                try:
                    obj = BaseEnergyDataSource.create_from_type(source_type, data_path, name=name)
                    obj.load_data()
                    sources.append(obj)
                except ValueError as e:
                    logger.error(f"Error loading data for {source_type} from {data_path}: {e}")
                    continue
                except FileNotFoundError as e:
                    logger.error(f"File not found for {source_type} at {data_path}: {e}")
                    continue
        logger.info(f"Total number of loaded experiments: {len(sources)}")
        return sources

