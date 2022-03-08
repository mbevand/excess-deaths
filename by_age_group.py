#!/usr/bin/python

import os, json, time, math, datetime
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Expected deaths for a given week can be calculated using 1 of 2 techniques:
# 'average': average of deaths on this week through 2015-2019
# 'linear_regression': calculate a linear regression on deaths recorded on
#   this week pre-pandemic, and project it to a year in the future; this helps
#   account for the trend of deaths over the years
predictor = 'linear_regression'

# Like the US CDC, we calculate excess deaths starting on year 2020 MMWR week 6,
# which starts on 02-Feb-2020
pandemic_start_week = (2020, 6)

# In Weekly_Counts_of_Deaths_by_Jurisdiction_and_Age.csv, CDC does not publish
# rows for weeks which had between 0 and 10 deaths, so if we do not find some
# of these rows, we assume 5 deaths (mean of 0-10)
suppressed_mean = 5

# If we calculate the absolute excess deaths for a particular age group for a
# particular state to be less than threshold, we ignore it and assume zero
# excess. This typically occurs when there are so few deaths that many
# rows in Weekly_Counts_of_Deaths_by_Jurisdiction_and_Age.csv are suppressed.
threshold = 10

# all_weeks is an array of the MMWR weeks (yyyy, mm): [(2015, 1), (2015, 2), ...]
# all_weeks_info maps an MMWR week (yyyy, mm) to its index in all_weeks[] and the saturday ending it:
#   { (2015, 1): {'idx': 0, 'end': '01/10/2015'}, ... }
all_weeks = []
all_weeks_info = {}
# my_excess contains our estimates of excess deaths; it maps an age group
# like "75-84 years" to an array of 4-tuple:
# (excess_per_1M, observed_deaths, expected_deaths, jurisdiction)
my_excess = None
# cdc_excess maps state names to the CDC's estimate of total number of excess deaths
cdc_excess = {}

# Population for US states, DC, Puerto Rico, the United States; by age group
# { 'Alabama': { '25-44 years': x, '45-64 years': x, ... },
#   ...
# }
pop = {}

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

def debug(s, end=None):
    return
    print(s, end=end)

def fmt(d):
    '''Parse a mm/dd/yyyy date and format it yyyy-mm-dd'''
    return datetime.datetime.strptime(d, '%m/%d/%Y').strftime('%Y-%m-%d')

def add_my(res, group, obs, exp, jurisdiction):
    if group not in res:
        res[group] = []
    if jurisdiction in ('New York', 'New York City'):
        # merge "New York City" and "New York"
        for (i, (epm2, obs2, exp2, jurisdiction2)) in enumerate(res[group]):
            if jurisdiction2 == 'New York':
                obs += obs2
                exp += exp2
                del res[group][i]
                break
        jurisdiction = 'New York'
    epm = (obs - exp) / pop[jurisdiction][group] * 1e6
    res[group].append((epm, obs, exp, jurisdiction))

def unsuppress(years, values):
    years2, values2 = [], []
    for yr in range(2015, pandemic_start_week[0]):
        if yr in years:
            values2.append(values.pop(0))
        else:
            values2.append(suppressed_mean)
        years2.append(yr)
    return years2, values2

def expected(df, wk):
    '''Return the expected number of deaths for week <wk>'''
    # not all years have MMWR week # 53, so we always predict
    # week 53 from week 52
    y, w = wk[0], min(wk[1], 52)
    # we calculate expected deaths using data predating the start of the pandemic
    mask = (df['Year'] < pandemic_start_week[0]) | \
          ((df['Year'] == pandemic_start_week[0]) & (df['Week'] < pandemic_start_week[1]))
    mask &= df['Week'] == w
    years = list(df[mask]['Year'])
    values = list(df[mask]['Number of Deaths'])
    years, values = unsuppress(years, values)
    if predictor == 'linear_regression':
        reg = LinearRegression().fit(np.reshape(years, (-1, 1)), np.reshape(values, (-1, 1)))
        e = reg.predict([[y]])[0][0]
    elif predictor == 'average':
        e = sum(values) / len(values)
    debug(f' [hist: ({years}) ({values})] expecting {e} for year {y}]', end='')
    return e

def analyze_group(res, df, jurisdiction, group):
    df = df[df['Age Group'] == group]
    df = df[['Year', 'Week', 'Number of Deaths']].sort_values(by=['Year', 'Week'])
    total_obs = total_exp = 0
    for i in range(all_weeks_info[pandemic_start_week]['idx'], len(all_weeks)):
        wk = all_weeks[i]
        debug(f'{jurisdiction} {group} processing {wk[0]}-{wk[1]} (#{i})', end='')
        mask = (df['Year'] == wk[0]) & (df['Week'] == wk[1])
        if not mask.any():
            obs = suppressed_mean
        else:
            obs = float(df[mask]['Number of Deaths'])
        exp = expected(df, wk)
        debug(f' obs {obs} exp {exp} excess {obs-exp}')
        total_obs += obs
        total_exp += exp
    if abs(total_obs - total_exp) < threshold:
        print(f'Ignoring {jurisdiction}/{group}: {total_obs - total_exp} excess deaths')
        return 0, 0
    add_my(res, group, total_obs, total_exp, jurisdiction)
    print(f'{(total_obs / total_exp - 1) * 100:.2f}% {jurisdiction} {group} {total_obs} {total_exp}')
    return total_obs, total_exp

def analyze_jurisdiction(res, df, jurisdiction):
    df = df[df['Jurisdiction'] == jurisdiction]
    total_obs = total_exp = 0
    for group in sorted(set(df['Age Group'])):
        obs, exp = analyze_group(res, df, jurisdiction, group)
        total_obs += obs
        total_exp += exp
    add_my(res, 'all', total_obs, total_exp, jurisdiction)
    print(f'{total_obs - total_exp:.0f} {(total_obs / total_exp - 1) * 100:.2f}% {jurisdiction}')

def get_all_weeks():
    # Get the list of all weeks defined in the dataset
    df = pd.read_csv('Weekly_Counts_of_Deaths_by_Jurisdiction_and_Age.csv')
    mask = df['Type'] == 'Predicted (weighted)'
    mask &= df['Jurisdiction'] == 'United States'
    mask &= df['Age Group'] == '85 years and older'
    _weeks = df[mask][['Week Ending Date', 'Year', 'Week']].sort_values(by=['Year', 'Week'])
    i = 0
    for _, row in _weeks.iterrows():
        y, w, end = row[['Year', 'Week', 'Week Ending Date']]
        all_weeks.append((y, w))
        all_weeks_info[(y, w)] = { 'idx': i, 'end': end }
        i += 1

def parse_pop():
    df = pd.read_csv('Population.csv')
    groups = {
            # do not use an upper bracket of 999 or higher as Population.csv
            # uses this value to mean "any age"
            'all': (0, 998),
            'Under 25 years': (0, 24),
            '25-44 years': (25, 44),
            '45-64 years': (45, 64),
            '65-74 years': (65, 74),
            '75-84 years': (75, 84),
            '85 years and older': (85, 998),
    }
    for jurisdiction in sorted(set(df['NAME'])):
        for (group, (a, b)) in groups.items():
            mask = (df['NAME'] == jurisdiction) & (df['SEX'] == 0) & \
                (df['AGE'] >= a) & (df['AGE'] <= b)
            n = int(df[mask][['POPEST2020_CIV']].sum())
            if jurisdiction not in pop:
                pop[jurisdiction] = {}
            pop[jurisdiction][group] = n
    # I could not find Puerto Rico demographics info by age group from the US
    # Census Bureau, so the data below is from
    # https://unstats.un.org/unsd/demographic-social/products/dyb/dybsets/2020.pdf
    # linked from
    # https://unstats.un.org/unsd/demographic-social/products/dyb/index.cshtml
    pop['Puerto Rico'] = {
            'all': 3_193_694,
            'Under 25 years': 21_386+96_096+157_661+182_764+201_616+216_485,
            '25-44 years': 219_925+185_241+189_502+198_881,
            '45-64 years': 204_152+211_903+219_296+209_130,
            '65-74 years': 189_933+176_557,
            '75-84 years': 131_326+90_644,
            '85 years and older': 91_196,
    }

def init():
    get_all_weeks()
    parse_pop()

def calc_excess():
    res = {}
    # Deaths by state and by age group. Source:
    # https://data.cdc.gov/NCHS/Weekly-Counts-of-Deaths-by-Jurisdiction-and-Age/y5bj-9g5w
    df = pd.read_csv('Weekly_Counts_of_Deaths_by_Jurisdiction_and_Age.csv')
    # keep rows that are not suppressed
    df = df[df['Suppress'].isnull()]
    # process number of deaths estimates, not raw (incomplete) number of deaths
    df = df[df['Type'] == 'Predicted (weighted)']
    for jurisdiction in sorted(set(df['Jurisdiction'])):
        analyze_jurisdiction(res, df, jurisdiction)
    return res

def load_cdc_official():
    # Excess death data. Source:
    # https://data.cdc.gov/NCHS/Excess-Deaths-Associated-with-COVID-19/xkkf-xrst/
    df = pd.read_csv('Excess_Deaths_Associated_with_COVID-19.csv')
    df = df[df['Outcome'] == 'All causes']
    df = df[df['Type'] == 'Predicted (weighted)']
    for st in sorted(set(df['State'])):
        e = int(df[df['State'] == st].iloc[0]['Total Excess Estimate'])
        if st in ('New York', 'New York City'):
            # merge "New York City" and "New York"
            st = 'New York'
            if st in cdc_excess:
                e += cdc_excess[st]
        cdc_excess[st] = e

def chart_group(group, l):
    def colname(st):
        if st not in party: return 'black'
        elif party[st] == 'democrat': return plt.cm.tab10(0)
        elif party[st] == 'republican': return plt.cm.tab10(3)
        else: raise Exception('unknown party {party[st]}')
    rcParams['font.family'] = ['serif']
    rcParams['font.serif'] = ['Latin Modern Math']
    (fig, ax) = plt.subplots(dpi=300, figsize=(6, 12))
    ys = [_[0] for _ in l]
    states = [f'{len(ys) - i}. ' + _[3] for (i, _) in enumerate(l)]
    colors = list(map(colname, [_[3] for _ in l]))
    missing = set(pop.keys()) - set([_[3] for _ in l])
    if missing:
        ys = [math.nan] * len(missing) + ys
        states = list(missing) + states
        colors = ['black'] * len(missing) + colors
    ax.barh(states, ys, color=colors)
    for (i, y) in enumerate(ys):
        if math.isnan(y):
            ax.text(0, i - .07, f'N/A (insufficient data)', va='center')
        else:
            ax.text(max(y, 0), i - .07, f' {y:,.0f}', va='center')
    ax.set_ylim(bottom=-1, top=len(ys))
    ax.set_xlim(left=min([0] + ys))
    ax.tick_params(axis='y', which='both', left=False)
    ax.set_xlabel('Excess deaths per million people')
    ax.set_title(f'Cumulative Excess Deaths per Capita\n'
            f'For Age Group "{group}"',
            fontsize='x-large', x=.35)
    for sp in ax.spines:
        ax.spines[sp].set_visible(False)
    fig.text(-.09, .06,
            'Source: https://github.com/mbevand/excess-deaths  '
            'Created by: Marc Bevand — @zorinaq\n'
            'Colors represent party of state governor as of 2022-01-01 '
            '(blue for democrat, red for republican)\nExcess mortality calculated '
            f'from week ending {fmt(all_weeks_info[pandemic_start_week]["end"])} '
            f'up to week ending {fmt(all_weeks_info[all_weeks[-1]]["end"])}',
            va='top', ha='left',
            bbox=dict(facecolor='white', edgecolor='none'))
    fig.savefig(f'by_age_group.{group}.png', bbox_inches='tight')

def chart():
    for g in my_excess.keys():
        my_excess[g].sort()
        print(f'== {g}')
        for (epm, obs, exp, jurisdiction) in my_excess[g]:
            print(f'{epm:5.0f} excess/1M {jurisdiction:20} {obs - exp:7.0f} excess')
        chart_group(g, my_excess[g])

def comp_cdc():
    f = open('by_age_group.csv', 'w')
    f.write('Jurisdiction,CDC Excess,Our Excess,Difference Percent,Our Excess Under 25,Our Excess 25-44,'
            'Our Excess 45-64,Our Excess 65-74,Our Excess 75-84,Our Excess 85+\n')
    for (epm, obs, exp, jurisdiction) in sorted(my_excess['all'], key=lambda x: -cdc_excess[x[3]]):
        cdc = cdc_excess[jurisdiction]
        our = round(obs - exp)
        f.write(f'{jurisdiction},{cdc},{our},{((our / cdc) - 1) * 100}')
        for group in ('Under 25 years', '25-44 years', '45-64 years', '65-74 years', '75-84 years', '85 years and older'):
            ff = list(filter(lambda x: x[3] == jurisdiction, my_excess[group]))
            if ff:
                _, obs, exp, _ = ff[0]
                f.write(f',{obs - exp:.0f}')
            else:
                f.write(',')
        f.write('\n')
    f.close()

def main():
    global my_excess
    init()
    cache = 'cache.by_age_group.json'
    if not os.path.exists(cache) or time.time() - os.path.getmtime(cache) > 3600:
        my_excess = calc_excess()
        json.dump(my_excess, open(cache, 'w'))
    else:
        my_excess = json.load(open(cache))
    load_cdc_official()
    comp_cdc()
    chart()

main()
