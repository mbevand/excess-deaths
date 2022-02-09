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

# Do age adjustment or not
do_age_adjust = True

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
        'Puerto Rico':3193694,
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

# Mean age of COVID deaths per state, from calc_age_of_deaths.py
mean_age_of_covid_deaths = {
  # Data as of 02/09/2022
  'Alaska': 68.37352138307553,
  'Hawaii': 69.08567774936061,
  'District of Columbia': 69.37536743092299,
  'New Mexico': 69.76144756277695,
  'Texas': 69.77144496798357,
  'Puerto Rico': 70.01070663811564,
  'Nevada': 70.62925861893623,
  'Georgia': 70.83748625240582,
  'Utah': 71.03945885005636,
  'Mississippi': 71.13578894133514,
  'Alabama': 71.18791030035439,
  'Arizona': 71.30838598736304,
  'Louisiana': 71.51842726263187,
  'Tennessee': 71.59209730383685,
  'California': 72.06366314411297,
  'South Carolina': 72.50149026361107,
  'Oklahoma': 72.53179505813954,
  'Arkansas': 72.74611138986452,
  'Florida': 72.91632948659414,
  'North Carolina': 73.06245571625057,
  'Kentucky': 73.25320051783659,
  'Washington': 73.40458488228005,
  'West Virginia': 73.51157365871164,
  'Oregon': 73.83295100770113,
  'Wyoming': 73.91129032258064,
  'Michigan': 73.93527810852186,
  'Colorado': 73.99450825857299,
  'Montana': 74.15857858484658,
  'Missouri': 74.32052190019613,
  'Maryland': 74.37574378718936,
  'Idaho': 74.41335540838853,
  'Virginia': 74.50151453369837,
  'Illinois': 74.85347265870521,
  'Kansas': 74.86937994071147,
  'Delaware': 75.09352101812573,
  'Indiana': 75.15678327645051,
  'New York': 75.18402280346778,
  'New Jersey': 75.2292904290429,
  'Nebraska': 75.25102459016394,
  'Ohio': 75.28756005713544,
  'Maine': 75.78601108033241,
  'South Dakota': 75.90250447227191,
  'Wisconsin': 76.00254087494477,
  'North Dakota': 76.38990638990639,
  'Pennsylvania': 76.45753459884047,
  'Minnesota': 76.98054425228891,
  'Iowa': 77.00310383747178,
  'Vermont': 77.2871287128713,
  'New Hampshire': 78.06266548984996,
  'Connecticut': 78.07352500748728,
  'Rhode Island': 78.56836953196697,
  'Massachusetts': 78.68565153733529,
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
    ret = _excess_for(df, state)
    ret += _excess_for(df, 'New York City') if state == 'New York' else 0
    return ret

def age_adjust(state):
    if not do_age_adjust:
        return 1
    # The IFR of COVID-19 increases approximately 1.115-fold with each year of
    # increase in age
    ifr_inc = 1.115
    return ifr_inc**(74 - mean_age_of_covid_deaths[state])

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
    ax.barh([f'{len(pop) - i}. {x[0]}' for (i, x) in enumerate(res)],
            [_[1] for _ in res], color=tableau20[6])
    for (i, (s, e)) in enumerate(res):
        ax.text(e + 50, i - .07, f'{e:,.0f}', va='center')
    ax.set_ylim(bottom=-1, top=len(pop))
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='y', which='both', left=False)
    ax.set_xlabel('Excess deaths per million people')
    xtra = ' (Age-Adjusted)' if do_age_adjust else ''
    ax.set_title(f'Cumulative Excess Deaths per Capita{xtra}\n'
            f'Since {start_date}', fontsize='x-large', x=.35)
    xtra = 'Age-adjustment is performed by normalizing each state\'s '\
            'excess deaths to what they would be\nif the mean '\
            'age of COVID deaths was 74 in all states.' if do_age_adjust else ''
    fig.text(-.09, .06,
            'Source: https://github.com/mbevand/excess-deaths  '
            'Created by: Marc Bevand — @zorinaq\n'
            f'Excess mortality calculated from week starting {start_date} '
            f'up to week ending {last}.\n'
            f'{xtra}',
            va='top', ha='left',
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
        res.append((st, excess_for(df, st) / pop[st] * 1e6 * age_adjust(st)))
    res = sorted(res, key=lambda x: x[1])
    for x in res:
        print(f'{x[1]:.0f} {x[0]}')
    # last week with data
    last = sorted(set(df['Week Ending Date']))[-1]
    chart(res, last)

main()
