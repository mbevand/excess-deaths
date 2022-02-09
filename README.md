*Updated: 09 Feb 2022*

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

For comparison, here is the same chart, same methodology, but counting all
excess deaths since the beginning of the pandemic:

![Cumulative excess deaths for each US state](eall.png)

## Methodology

### Excess deaths

We take [deaths reported by the US CDC, per state, per
week](https://data.cdc.gov/NCHS/Excess-Deaths-Associated-with-COVID-19/xkkf-xrst/)
(column "Observed Number" where "Type" is "Predicted (weighted)"). The US
CDC weighted these figures to account for reporting delays. This
affects only data from the last few weeks. In our experience, weighted vs
unweighted has little impact on the charts above.

For each week **since 2020-04-26** we calculate the difference between reported
deaths and the average expected number of deaths from the US CDC (column
"Average Expected Count"). The difference can be positive or negative.

We add up these differences to calculate the final cumulative excess deaths
per capita.  Then we perform age-adjustment:

### Age-adjustment

Age-adjustment is based on a simple premise: the difference in mean age of
COVID deaths in 2 states is the difference in mean age of COVID infections
in these 2 states. For example the mean age of COVID deaths may be 72.1 in
California, and 74.0 in Colorado, therefore we assume a 1.9 years difference in
the mean age of infections in these 2 states. The mean age of infections is
significantly younger than the mean age of deaths, but the exact value is not
relevant.

The age-adjustment is thus simple to perform. In the above example, we would
calculate theoretical COVID deaths by shifting infections in California 1.9
years upward. We know that an extra 1.9 years of age would increase risk of death
by 1.23x (for example), therefore to compare California to Colorado, we would multiply
California's excess deaths by 1.23x.

The exact details of the calculations are described below:

Firstly we determine by how much the IFR of COVID-19
increases with each year of age. As per [O’Driscoll et al.: Age-specific mortality and immunity patterns of SARS-CoV-2](https://www.nature.com/articles/s41586-020-2918-0), in [Supplementary information](https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-020-2918-0/MediaObjects/41586_2020_2918_MOESM1_ESM.pdf) (table S3):

* IFR for ages 65-69 = 1.075%
* IFR for ages 75-79 = 3.203%

On this 10-year range, which spans the approximate mean age of COVID death
among the states (68 to 79 years), the IFR increases by: (3.203 / 1.075) ^ (1 /
10) = 1.115-fold with each year of age. We term this factor **ifr_inc**.

Secondly, for each state, we determine the mean age of COVID deaths.
This is calculated from the [CDC dataset "Provisional COVID-19 Deaths by Sex
and Age"](https://data.cdc.gov/NCHS/Provisional-COVID-19-Deaths-by-Sex-and-Age/9bhg-hcku)
by the script [calc_age_of_deaths.py](calc_age_of_deaths.py).

Thirdly, each state is adjusted by normalizing its excess deaths to what it
would be if the mean age of COVID deaths was 74 (an arbitrary value).
Concretely, excess deaths are simply mutiplied by:

ifr_inc ^ (74 - mean_age_of_covid_deaths)

### Population

To calculate excess mortality per capita, we use states population from the [US
Census Bureau 2019 estimates](https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/state/detail/SCPRC-EST2019-18+POP-RES.csv).
