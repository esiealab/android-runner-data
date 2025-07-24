import matplotlib.pyplot as plt
from typing import List
from .base_energy_data_source import BaseEnergyDataSource

class DataSourcePlotter:
    def __init__(self, sources: List[BaseEnergyDataSource]):
        self.sources = sources

    def plot_power(self, title: str = "Power vs Time", show: bool = True):
        """
        Concatenate and plot the power of each source on the same graph.
        """
        plt.figure(figsize=(10, 6))
        for ds in self.sources:
            if ds.data is not None and not ds.data.empty:
                x = ds.data["Timestamp"]
                y = ds.data["PowerWatts"]
                plt.plot(x, y, label=f"{ds.name} ({ds.start_time}) - [{ds.source}]")
        plt.xlabel("Timestamp")
        plt.ylabel("Power (W)")
        plt.title(title)
        plt.legend()
        plt.grid(True)
        if show:
            plt.show()
        return plt.gcf()
