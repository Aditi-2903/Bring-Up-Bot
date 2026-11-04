# Answer keys (for scoring only: the agent must never read this file)

| Scenario | Symptom the user reports | Root cause | Fix in `config.json` | Datasheet evidence | Verification |
|---|---|---|---|---|---|
| wrong_address | App errors: no response from address | `i2c_address` is 0x38; part `ABP2DSNT001BD2A3XX` output type "2" = 0x28, and `i2cdetect -y 1` shows 28 | `"i2c_address": "0x28"` | Nomenclature (p8): output type 2 = I2C address 0x28; default address 0x28 (p26) | `check_abp2.py` PASS and app reads ~0 bar |
| gage_range | App reads ~+0.5 bar with both ports at room air | `pressure_min_bar` is 0.0; range code 001BD = ±1 bar differential | `"pressure_min_bar": -1.0` | Pressure range table (p8/p11): 001BD = -1 to 1 bar | `check_abp2.py` PASS and app reads ~0 bar |
| no_wait (test first) | Busy warning or stale/odd readings | `conversion_wait_ms` is 0; sensor needs ≥5 ms or busy bit clear | `"conversion_wait_ms": 10` | p27: wait for busy flag to clear or at least 5 ms | No busy warning; `check_abp2.py` PASS |
