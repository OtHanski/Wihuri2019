Current functional version:

-PSUN8731A-CTRLv31 for free control measurements (sweeps undergoing work)
-MeasInductance to determine coil inductance and resistance.

PSUN8731A-CTRLv31 README:
-In current version sweeps were removed due to being clunky and unnecessary.
-Good for collecting freeform data
-Currently plots (manually exportable) I(V), V(t) and I(t), can be set to save all data gathered automatically to txt.
-Main controls allow setting voltage/current limits for PSU and overall measurement frequency.
-Other controls include options for protection, Voltage measurement source and saved data file name.

MeasInductance README:
-Before making measurement, one should figure out a safe current/voltage level the coil can be driven to straight from
 zero. The higher the current, the more accurate the measurement is.
-Averaging may be used to improve accuracy, with long enough measurements and averaging at least 3 digits
 accuracy can be reached.

... wip