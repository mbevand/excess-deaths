*Updated: 31 Jan 2022*

Author: Marc Bevand

This repository analyzes cumulative excess deaths for each US state, excluding
the first 8 weeks of the COVID-19 pandemic in order to focus on
long-term excess deaths.

Long-term excess deaths are defined as roughly deaths from second half of the
first wave (Spring 2020), plus all deaths from subsequent waves.

Long-term excess deaths are an indirect result of each state's long-term plan
and measures against the pandemic.

## Chart

![Cumulative excess deaths for each US state](e.png)

## Methodology

We take [deaths reported by the US
CDC](https://data.cdc.gov/NCHS/Excess-Deaths-Associated-with-COVID-19/xkkf-xrst/)
(column "Observed Number" where "Type" is "Predicted (weighted)"). The US
CDC weighted these figures to account for reporting delays. This
affects only data from the last few weeks. In our experience, weighted vs
unweighted has little impact on the chart above.

For each week **since 2020-04-26** we calculate the difference between reported
deaths and the average expected number of deaths from the US CDC (column
"Average Expected Count"). The difference can be positive or negative.

We add up these differences to calculate the final cumulative excess deaths
per capita.

States population data is from the [US Census Bureau 2019 estimates](https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/state/detail/SCPRC-EST2019-18+POP-RES.csv).
