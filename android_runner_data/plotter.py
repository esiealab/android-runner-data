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
    
    def plot_fft(self, title: str = "FFT of Power vs Frequency", show: bool = True, freq_min: float = None, freq_max: float = None):
        """
        Plot the FFT (Fast Fourier Transform) of the power data for each source,
        using the DataFrame stored in the power_fft attribute.
        Optionally, only display data within [freq_min, freq_max].
        """
        plt.figure(figsize=(10, 6))
        for ds in self.sources:
            df_fft = getattr(ds, "power_fft", None)
            if df_fft is not None and not df_fft.empty:
                df_plot = df_fft
                if freq_min is not None:
                    df_plot = df_plot[df_plot["frequency"] >= freq_min]
                if freq_max is not None:
                    df_plot = df_plot[df_plot["frequency"] <= freq_max]
                plt.plot(df_plot["frequency"], df_plot["fft_magnitude"],
                         label=f"{ds.name} ({ds.start_time}) - [{ds.source}]")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("FFT Magnitude")
        plt.title(title)
        plt.legend()
        plt.grid(True)
        if show:
            plt.show()
        return plt.gcf()