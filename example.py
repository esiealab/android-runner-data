import pandas as pd
from android_runner_data import BaseEnergyDataSource
from android_runner_data.plotter import DataSourcePlotter

# Direct definition of the list of experiments
EXPERIMENTS = [
    {
        "name": "BatteryManager TikTok",
        "source_type": "batterymanager",
        "data_path": "experience/data/Pixel3W/com-zhiliaoapp-musically/batterymanager"
    },
    {
        "name": "WattoMeter TikTok",
        "source_type": "wattometer",
        "data_path_global": "Resultat_campagne_Pixel3_avec_stalkerware/TikTok/output",
        "data_path": "data/Pixel3W/com-zhiliaoapp-musically/wattometer"
    }
]

import logging
logging.getLogger("android_runner_data").setLevel(logging.INFO)

# Load experiments using the static method
data_sources = BaseEnergyDataSource.load_experiments(EXPERIMENTS)

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
plotter.plot_power(title="Comparison of measured power")
