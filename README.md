*Updated: 07 Mar 2022*

Author: Marc Bevand

This repository analyzes cumulative excess deaths for each US state.

## Excess deaths since the start of the pandemic

Excess deaths since 2020-02-02:

![Cumulative excess deaths for each US state](all_ages.full.png)

## "Long-term" excess deaths

Long-term excess deaths are defined as excess deaths after 2020-04-26 (roughly
peak deaths of the first wave in Spring 2020). Long-term excess deaths are an
indirect result of each state's long-term plan and interventions against the
pandemic:

![Cumulative excess deaths for each US state](all_ages.longterm.png)

## Methodology

### Excess deaths

We take [deaths reported by the US CDC, per state, per
week](https://data.cdc.gov/NCHS/Excess-Deaths-Associated-with-COVID-19/xkkf-xrst/)
(column "Observed Number" where "Type" is "Predicted (weighted)"). The US
CDC weighted these figures to account for reporting delays. This
affects only data from the last few weeks. In our experience, weighted vs
unweighted has little impact on the charts above.

For each week we calculate the difference between reported
deaths and the average expected number of deaths from the US CDC (column
"Average Expected Count"). The difference can be positive or negative.

We add up these differences to calculate the final cumulative excess deaths
per capita.

### Population

In `all_ages.py`, to calculate excess mortality per capita, we use states population from the [US
Census Bureau 2019 estimates](https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/state/detail/SCPRC-EST2019-18+POP-RES.csv).

In `by_age_group.py` we use state population from the [US
Census Bureau 2020 estimates](https://www.census.gov/programs-surveys/popest/technical-documentation/research/evaluation-estimates/2020-evaluation-estimates/2010s-state-detail.html), file [Single Year of Age and Sex for the Civilian Population](https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/state/asrh/SC-EST2020-AGESEX-CIV.csv)
