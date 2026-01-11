Dataset: ERA5 reanalysis
Region: Uttarakhand (28.0–31.5N, 77.0–81.0E)
Temporal resolution: Hourly
Period: 2005–2024
Variables:
- t2m: 2m air temperature (K)
- u10, v10: 10m wind components (m/s)
- sp: surface pressure (Pa)
- tcwv: total column water vapour (kg/m²)
- tp: total precipitation (m)

Spatial aggregation:
- Instant variables: spatial mean
- Accumulated variables: spatial sum

Temporal alignment:
- valid_time → time
- timestamps floored to hourly grid
