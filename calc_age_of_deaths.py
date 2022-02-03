#!/usr/bin/python

import math
import numpy as np
import pandas as pd

mean_age_of_covid_deaths = {}

def calc_state(state, df):
    if state == 'New York City':
        return
    elif state == 'New York':
        states = ['New York', 'New York City']
    else:
        states = [state]
    # Map age groups to average age in this group
    groups = {
            'Under 1 year': 0.5,
            '1-4 years':    3,
            '5-14 years':   10,
            '15-24 years':  20,
            '25-34 years':  30,
            '35-44 years':  40,
            '45-54 years':  50,
            '55-64 years':  60,
            '65-74 years':  70,
            '75-84 years':  80,
            '85 years and over': 90,
            # For correctness, 90 should be replaced with the mean age
            # of the person of age 85+
            }
    sum_ages = 0
    sum_deaths = 0
    for _s in states:
        for c, m in groups.items():
            deaths = float(df[(df['State'] == _s) & (df['Age Group'] == c)]
                    ['COVID-19 Deaths'])
            if math.isnan(deaths):
                # Cells with counts between 1-9 are typically suppressed (NaN),
                # so we assume 5
                # Note: assuming 0 or 5 has insignificant effect on the mean
                # age of deaths
                deaths = 5
            sum_ages += m * deaths
            sum_deaths += deaths
    mean_age_of_covid_deaths[state] = sum_ages / sum_deaths

def main():
    df = pd.read_csv('Provisional_COVID-19_Deaths_by_Sex_and_Age.csv')
    df = df[df['Group'] == 'By Total']
    df = df[df['Sex'] == 'All Sexes']
    df = df[df['State'] != 'United States']
    for state in set(df['State']):
        calc_state(state, df)
    as_of = list(set(df['Data As Of']))
    assert(len(as_of) == 1)
    as_of = as_of[0]
    print("mean_age_of_covid_deaths = {\n  # Data as of", as_of)
    for (a, b) in sorted(mean_age_of_covid_deaths.items(), key=lambda f: f[1]):
        print(f'  \'{a}\': {b},')
    print('}')

main()
