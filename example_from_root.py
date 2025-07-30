import pandas as pd
from android_runner_data import BaseEnergyDataSource
from android_runner_data.plotter import DataSourcePlotter

# Direct definition of the list of experiments
EXPERIMENTS_ROOT = [
    {
        "handle_duplicates": False,
        "name": "[AVEC] TikTok",
        "data_path": "datas/Resultat_campagne_Pixel3_avec/TikTok/"
    },
    {
        "handle_duplicates": False,
        "name": "[SANS] TikTok",
        "data_path": "datas/Resultat_campagne_Pixel3_sans/TikTok/"
    }
]

import logging
logging.getLogger("android_runner_data").setLevel(logging.INFO)

# Load experiments using the static method
data_sources = BaseEnergyDataSource.load_experiments_from_root(EXPERIMENTS_ROOT)

# Summary table
summary = []
for ds in data_sources:
    summary.append({
        "Name": ds.name,
        "Source": ds.source,
        "File": ds.data_file_name,
        "Start Time": ds.start_time,
        "Duration (s)": ds.duration_seconds,
        "Energy (Wh)": ds.energy_wh,
        "Energy (J)": ds.energy_joules,
        "Average Power (W)": ds.power_avg, 
        "Min Power (W)": ds.power_min,
        "Max Power (W)": ds.power_max,
        "Std Power (W)": ds.power_std
    })
summary_df = pd.DataFrame(summary)
print("Summary of Experiments:")
print(summary_df)

# Plot power for all sources
plotter = DataSourcePlotter(data_sources)
plotter.plot_power(title="Comparison of measured power", show=False)
plotter.plot_fft(title="Comparison of FFT of power", show=False)
plotter.plot_fft(title="Comparison of FFT of power with frequency limits", show=True, freq_min=0.1, freq_max=10.0)