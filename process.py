#!/usr/bin/python

import math, sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# If weighted is True, use the CDC's estimates of deaths that attempt to
# correct for reporting delays; if False, use raw (incomplete) death figures
weighted = True

# Define excess deaths as those above the upper bound of the 95% prediction
# interval ('Upper Bound Threshold'), or as those above the expected number of
# deaths ('Average Expected Count')
baseline = 'Average Expected Count'

# Calculate excess deaths since the week starting on... (must be a Sunday)
start_date = sys.argv[1] if len(sys.argv) > 1 else '2020-04-26'

# U.S. Census Bureau’s population estimates for US states and DC, as of 2019.
# Source:
# https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/state/detail/SCPRC-EST2019-18+POP-RES.csv
pop = {
        'Alabama':4903185,
        'Alaska':731545,
        'Arizona':7278717,
        'Arkansas':3017804,
        'California':39512223,
        'Colorado':5758736,
        'Connecticut':3565287,
        'Delaware':973764,
        'District of Columbia':705749,
        'Florida':21477737,
        'Georgia':10617423,
        'Hawaii':1415872,
        'Idaho':1787065,
        'Illinois':12671821,
        'Indiana':6732219,
        'Iowa':3155070,
        'Kansas':2913314,
        'Kentucky':4467673,
        'Louisiana':4648794,
        'Maine':1344212,
        'Maryland':6045680,
        'Massachusetts':6892503,
        'Michigan':9986857,
        'Minnesota':5639632,
        'Mississippi':2976149,
        'Missouri':6137428,
        'Montana':1068778,
        'Nebraska':1934408,
        'Nevada':3080156,
        'New Hampshire':1359711,
        'New Jersey':8882190,
        'New Mexico':2096829,
        'New York':19453561,
        'North Carolina':10488084,
        'North Dakota':762062,
        'Ohio':11689100,
        'Oklahoma':3956971,
        'Oregon':4217737,
        'Pennsylvania':12801989,
        'Rhode Island':1059361,
        'South Carolina':5148714,
        'South Dakota':884659,
        'Tennessee':6829174,
        'Texas':28995881,
        'Utah':3205958,
        'Vermont':623989,
        'Virginia':8535519,
        'Washington':7614893,
        'West Virginia':1792147,
        'Wisconsin':5822434,
        'Wyoming':578759,
}

def excess_for(df, state):
    def _excess_for(df, state):
        if weighted:
            df = df[df['Type'] == 'Predicted (weighted)']
            # 'Observed Number' is adjusted to account for reporting delays
        else:
            df = df[df['Type'] == 'Unweighted']
            # 'Observed Number' is the (incomplete) number of deaths
        df = df[df['Week Ending Date'] >= start_date]
        df = df[df['State'] == state]
        cum_excess = 0
        for _, row in df.iterrows():
            o = row['Observed Number']
            b = row[baseline]
            # For small states, the CDC sometimes suppresses data for the last
            # week or 2 as data is so incomplete it cannot be weighted/adjusted
            # in which case we just skip over these states & weeks
            if math.isnan(o):
                continue
            # When calculating excess deaths based on Average Expected Count,
            # weeks may have positive or negative excess deaths. But when
            # calculating based on the upper bound of the 95% prediction
            # interval, we obviously only account for positive excess.
            if baseline == 'Average Expected Count' or o - b > 0:
                cum_excess += o - b
        return cum_excess
    # For some reason the CDC splits NY state into the city ('New York City')
    # and the rest of the state ('New York')
    ret = _excess_for(df, 'New York City') if state == 'New York' else 0
    return ret + _excess_for(df, state)

def chart(res, last):
    # "Tableau 20" colors
    tableau20 = [(x[0] / 255., x[1] / 255., x[2] / 255.) for x in
                 [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                  (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                  (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                  (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                  (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]]
    rcParams['font.family'] = ['serif']
    rcParams['font.serif'] = ['Latin Modern Math']
    (fig, ax) = plt.subplots(dpi=300, figsize=(6, 12))
    ax.barh([_[0] for _ in res], [_[1] for _ in res], color=tableau20[6])
    for (i, (s, e)) in enumerate(res):
        ax.text(e + 50, i - .07, f'{e:,.0f}', va='center')
    ax.set_ylim(bottom=-1, top=51)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='y', which='both', left=False)
    ax.set_xlabel('Excess deaths per million people')
    ax.set_title(f'Cumulative Excess Deaths per Capita,\n'
            'After First 8 Weeks of the Pandemic', fontsize='x-large')
    fig.text(0, .06,
            f'Excess deaths data from US CDC, from week starting {start_date} up '
            f'to week ending {last}.\n'
            'Population data from US Census Bureau 2019 estimates.\n'
            'Created by: Marc Bevand — @zorinaq',
            fontsize='small', va='top', ha='left',
            bbox=dict(facecolor='white', edgecolor='none'))
    fig.savefig('e.png', bbox_inches='tight')

def main():
    # Excess death data. Source:
    # https://data.cdc.gov/NCHS/Excess-Deaths-Associated-with-COVID-19/xkkf-xrst/
    df = pd.read_csv('data.csv')
    # A short description of the most important columns in the CSV file:
    # - Observed Number: observed number of deaths
    # - Upper Bound Threshold: upper bound of 95% prediction interval of
    #   expected deaths
    # - Average Expected Count: average expected number of deaths
    # - Exceeds Threshold: boolean representing Observed Number > Upper Bound
    #   Threshold
    # - Excess Estimate: Observed Number minus Average Expected Count
    #   (clamped to 0 if negative)
    # - Total Excess Estimate: sum of Excess Estimate for week ending 2/1/2020
    #   and later
    df = df[df['Outcome'] == 'All causes']
    res = []
    for st in pop.keys():
        # calculate cumulative excess deaths per million capita
        res.append((st, excess_for(df, st) / pop[st] * 1e6))
    res = sorted(res, key=lambda x: x[1])
    for x in res:
        print(f'{x[1]:.0f} {x[0]}')
    # last week with data
    last = sorted(set(df['Week Ending Date']))[-1]
    chart(res, last)

main()
