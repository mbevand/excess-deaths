*Updated: 01 Feb 2022*

Author: Marc Bevand

This repository analyzes cumulative excess deaths for each US state, excluding
the first 8 weeks of the COVID-19 pandemic in order to focus on
long-term excess deaths.

Long-term excess deaths are defined as deaths after 2020-04-26, roughly the
second half of the first wave (Spring 2020), plus all deaths from subsequent
waves.

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

Then we perform age-adjustment. First we determine by how much the IFR of COVID-19
increases with each year of age. As per [O’Driscoll et al.: Age-specific mortality and immunity patterns of SARS-CoV-2](https://www.nature.com/articles/s41586-020-2918-0), in [Supplementary information](https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-020-2918-0/MediaObjects/41586_2020_2918_MOESM1_ESM.pdf) (table S3):

* IFR for ages 30-34 = 0.024%
* IFR for ages 75-79 = 3.203%

On this 45-year range, the IFR increases by: (3.203 / 0.024)^(1 / 45) =
1.115-fold with each year of increase. We term this factor **ifr_inc**.

Secondly, each state is adjusted by normalizing its
excess deaths to what it would be if the median age was 40 (an arbitrary
value). We do this by mutiplying excess death by:

ifr_inc ^ (40 - state_median_age)

States population and median age data is from the [US Census Bureau 2019 estimates](https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/state/detail/SCPRC-EST2019-18+POP-RES.csv).
