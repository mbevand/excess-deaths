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
  # Data as of 02/16/2022
  'Alaska': 68.4322033898305,
  'District of Columbia': 69.34827182190978,
  'Hawaii': 69.3898931799507,
  'Texas': 69.76863481558416,
  'New Mexico': 69.77740719257541,
  'Puerto Rico': 70.01070663811564,
  'Nevada': 70.669473789117,
  'Georgia': 70.8611710375514,
  'Utah': 71.13448056086679,
  'Mississippi': 71.1884739055157,
  'Alabama': 71.21794508113015,
  'Arizona': 71.32640442821811,
  'Louisiana': 71.53041955641008,
  'Tennessee': 71.62596891016138,
  'California': 72.09816374430484,
  'South Carolina': 72.38316450189546,
  'Oklahoma': 72.51854599406528,
  'Arkansas': 72.76708984375,
  'Florida': 72.94673064918851,
  'North Carolina': 73.06145170017064,
  'Kentucky': 73.2342118174809,
  'Washington': 73.44950376768976,
  'West Virginia': 73.51540616246498,
  'Oregon': 73.83056719303899,
  'Wyoming': 73.8671096345515,
  'Michigan': 73.93562037935303,
  'Colorado': 73.97524833757491,
  'Montana': 74.15845395749923,
  'Missouri': 74.288857478131,
  'Maryland': 74.37345467032966,
  'Idaho': 74.38178462874511,
  'Virginia': 74.47804368685443,
  'Kansas': 74.8355623100304,
  'Illinois': 74.84165944003965,
  'Delaware': 74.95607476635514,
  'Indiana': 75.04105316269896,
  'New York': 75.19784041263023,
  'New Jersey': 75.21680150761932,
  'Nebraska': 75.26056649701262,
  'Ohio': 75.26812200502016,
  'Maine': 75.59683177153056,
  'South Dakota': 75.8833392163784,
  'Wisconsin': 75.97600260605184,
  'North Dakota': 76.3614360629286,
  'Pennsylvania': 76.43754887079712,
  'Minnesota': 76.93167624281789,
  'Iowa': 76.96844038739842,
  'Vermont': 77.27611940298507,
  'Connecticut': 78.00512445095168,
  'New Hampshire': 78.03200692041523,
  'Rhode Island': 78.42136323399232,
  'Massachusetts': 78.65621031975067,
}

# Party of governors, as of 01-Jan-2022
party = {
  'Alabama': 'republican',
  'Alaska': 'republican',
  'Arizona': 'republican',
  'Arkansas': 'republican',
  'California': 'democrat',
  'Colorado': 'democrat',
  'Connecticut': 'democrat',
  'Delaware': 'democrat',
  'Florida': 'republican',
  'Georgia': 'republican',
  'Hawaii': 'democrat',
  'Idaho': 'republican',
  'Illinois': 'democrat',
  'Indiana': 'republican',
  'Iowa': 'republican',
  'Kansas': 'democrat',
  'Kentucky': 'democrat',
  'Louisiana': 'democrat',
  'Maine': 'democrat',
  'Maryland': 'republican',
  'Massachusetts': 'republican',
  'Michigan': 'democrat',
  'Minnesota': 'democrat',
  'Mississippi': 'republican',
  'Missouri': 'republican',
  'Montana': 'republican',
  'Nebraska': 'republican',
  'Nevada': 'democrat',
  'New Hampshire': 'republican',
  'New Jersey': 'democrat',
  'New Mexico': 'democrat',
  'New York': 'democrat',
  'North Carolina': 'democrat',
  'North Dakota': 'republican',
  'Ohio': 'republican',
  'Oklahoma': 'republican',
  'Oregon': 'democrat',
  'Pennsylvania': 'democrat',
  'Rhode Island': 'democrat',
  'South Carolina': 'republican',
  'South Dakota': 'republican',
  'Tennessee': 'republican',
  'Texas': 'republican',
  'Utah': 'republican',
  'Vermont': 'republican',
  'Virginia': 'democrat',
  'Washington': 'democrat',
  'West Virginia': 'republican',
  'Wisconsin': 'democrat',
  'Wyoming': 'republican',
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
    # res is an array of (state, excess_per_M) tuples
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
    colors = []
    for (state, _) in res:
        if state not in party:
            colors.append((.1, .1, .1))
        elif party[state] == 'democrat':
            colors.append(tableau20[0])
        elif party[state] == 'republican':
            colors.append(tableau20[6])
    ax.barh([f'{len(pop) - i}. {x[0]}' for (i, x) in enumerate(res)],
            [_[1] for _ in res], color=colors)
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
            'Colors represent party of state governor as of 2022-01-01 '
            '(blue for democrat, red for republican)\n'
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
