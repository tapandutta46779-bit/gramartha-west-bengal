# Demand Model

The operational baseline consumes a source-linked `monthly_dairy_demand_litres` interval. The HCES
importer computes survey-weighted monthly per-capita quantity and expenditure priors by available
district/NSS-region/rural-urban cells, normalizing recall periods. These remain sampled priors—not
village observations—and are not run until authenticated official files are supplied.

No demand ML model is trained because no defensible locality target is currently available.

