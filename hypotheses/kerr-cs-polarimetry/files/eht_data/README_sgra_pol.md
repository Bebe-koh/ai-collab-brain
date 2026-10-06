# EHT Sagittarius A&ast; Polarized Data

**Authors:** The Event Horizon Telescope Collaboration et al.

**Date:** March 27, 2024

**Primary Reference:** [The Event Horizon Telescope Collaboration, et al. 2024b, ApJL, 964, L25 (Sgr A&ast; Paper VII)](https://doi.org/10.3847/2041-8213/ad2df0)

**Data Product Code:** [2024-D02-01](https://eventhorizontelescope.org/for-astronomers/data)

**Brief Description:**

We release a calibrated polarimetric data set to accompany tthe First SgrA&ast; Event
Horizon Telescope Polarization Results paper series (EHT Collaboration et al. 2024b,c).
The data set is derived from the Rev7 Correlation of the Event Horizon Telescope (EHT)'s
April 2017 observation campaign (EHT Collaboration et al. 2019c), with further processing
and science validation as described in EHT Collaboration et al. 2022b.

This data set contains Sagittarius A&ast; (Sgr A&ast;) data for both low and high bands for
two observed days (April 6th and 7th, 2017). This release includes the fringe fitted,
a-priori calibrated, and network calibrated data from both the EHT-HOPS and rPICARD (CASA)
pipelines, which are used in the First Sgr A&ast; EHT results, with the addition of absolute
EVPA calibration from ALMA, parallactic angle rotation, and D-term calibration using the
M87-derived leakage solutions (EHT Collaboration et al. 2021a). Independent flux calibration
is performed based on estimated station sensitvities during the campaign (Issaoun et al. 2017,
Janssen et al. 2019, Wielgus et al. 2022).  Data were further calibrated to apply polarimetric
gains to remove R-L gain offsets, amplitude gains obtained from calibrators, amplitude gains
on LMT for its rapid gain fluctuations, and phase gains on JCMT for its residual phase
fluctuations. A description of the data properties, their validation, and estimated systematic
errors is given in M87 Paper III and Sgr A* Paper II and Paper III with additional details in
Wielgus et al. (2019) and Wielgus et al. (2022). The data are time averaged to 10 seconds and
frequency averaged over all 32 intermediate frequencies (IFs). The R/L complex gains have been
calibrated assuming the intrinsic Stokes V visibilities are zero.


**File Name Convention:**

The data files are named in the following convention:

    [Data-Release-Tag]_[Source]_[year]_[day-of-year]_[band]_[pipeline]_[stages].[format]

**Station Code Table:**

| UVFITS Code | Station Name                  | Location   |
| ----------- | ----------------------------- | ---------- |
| AA          | ALMA                          | Chile      |
| AP          | APEX                          | Chile      |
| AZ          | Submillimeter Telescope       | Arizona    |
| JC          | James Clerk Maxwell Telescope | Hawai'i    |
| LM          | Large Millimeter Telescope    | Mexico     |
| PV          | IRAM                          | Spain      |
| SM          | Submillimeter Array           | Hawai'i    |
| SP          | South Pole Telescope          | Antarctica |

**References:**

- [EHT Collaboration Data Portal Website](https://eventhorizontelescope.org/for-astronomers/data)
- [The Event Horizon Telescope Collaboration, et al. 2019a, ApJL, 875, L1 (M87 Paper I)](https://doi.org/10.3847/2041-8213/ab0ec7)
- [The Event Horizon Telescope Collaboration, et al. 2019b, ApJL, 875, L2 (M87 Paper II)](https://doi.org/10.3847/2041-8213/ab0c96)
- [The Event Horizon Telescope Collaboration, et al. 2019c, ApJL, 875, L3 (M87 Paper III)](https://doi.org/10.3847/2041-8213/ab0c57)
- [The Event Horizon Telescope Collaboration, et al. 2019d, ApJL, 875, L4 (M87 Paper IV)](https://doi.org/10.3847/2041-8213/ab0e85)
- [The Event Horizon Telescope Collaboration, et al. 2019e, ApJL, 875, L5 (M87 Paper V)](https://doi.org/10.3847/2041-8213/ab0f43)
- [The Event Horizon Telescope Collaboration, et al. 2019f, ApJL, 875, L6 (M87 Paper VI)](https://doi.org/10.3847/2041-8213/ab1141)
- [The Event Horizon Telescope Collaboration, et al. 2021a, ApJL, 910, L12 (M87 Paper VII)](https://doi.org/10.3847/2041-8213/abe71d)
- [The Event Horizon Telescope Collaboration, et al. 2021b, ApJL, 910, L13 (M87 Paper VIII)](https://doi.org/10.3847/2041-8213/abe4de)
- [The Event Horizon Telescope Collaboration, et al. 2023, ApJL, 957, L20 (M87 Paper IX)](https://doi.org/10.3847/2041-8213/acff70)
- [Blackburn, L., Chan, C.-k., Crew, G., et al. 2019, ApJ, 882, 23](https://doi.org/10.3847/1538-4357/ab328d)
- [Janssen, M., Goddi, C., van Bemmel, I., et al. 2019, A&A, 626A, 75](https://doi.org/10.1051/0004-6361/201935181)
- [Issaoun, S., Folkers, T., Blackburn, L., et al. 2017, EHT Memo 2017-CE-02](https://eventhorizontelescope.org/for-astronomers/memos)
- [Janssen, M., Blackburn, L., Issaoun, S., et al. 2019, EHT Memo 2019-CE-01](https://eventhorizontelescope.org/for-astronomers/memos)
- [Wielgus, M., Blackburn, L., Issaoun, S., et al. 2019, EHT Memo 2019-CE-02](https://eventhorizontelescope.org/for-astronomers/memos)
- [The Event Horizon Telescope Collaboration, et al. 2022a, ApJL, 930, L12 (Sgr A&ast; Paper I)](https://doi.org/10.3847/2041-8213/ac6674)
- [The Event Horizon Telescope Collaboration, et al. 2022b, ApJL, 930, L13 (Sgr A&ast; Paper II)](https://doi.org/10.3847/2041-8213/ac6675)
- [The Event Horizon Telescope Collaboration, et al. 2022c, ApJL, 930, L14 (Sgr A&ast; Paper III)](https://doi.org/10.3847/2041-8213/ac6429)
- [The Event Horizon Telescope Collaboration, et al. 2022d, ApJL, 930, L15 (Sgr A&ast; Paper IV)](https://doi.org/10.3847/2041-8213/ac6736)
- [The Event Horizon Telescope Collaboration, et al. 2022e, ApJL, 930, L16 (Sgr A&ast; Paper V)](https://doi.org/10.3847/2041-8213/ac6672)
- [The Event Horizon Telescope Collaboration, et al. 2022f, ApJL, 930, L17 (Sgr A&ast; Paper VI)](https://doi.org/10.3847/2041-8213/ac6756)
- [The Event Horizon Telescope Collaboration, et al. 2024b, ApJL, 964, L25 (Sgr A&ast; Paper VII)](https://doi.org/10.3847/2041-8213/ad2df0)
- [The Event Horizon Telescope Collaboration, et al. 2024c, ApJL, 964, L26 (Sgr A&ast; Paper VIII)](https://doi.org/10.3847/2041-8213/ad2df1)
- [Wielgus, M., Marchili, N., Marti-Vidal, I., Keating, G.K., Ramakrishnan, V., et al. 2022, ApJL, 930, L19](https://doi.org/10.3847/2041-8213/ac6428)
