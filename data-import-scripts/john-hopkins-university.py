# For the John Hopkins data we publish the three single datasets for global confirmed cases, deaths and recovered,
# but then also one merged dataset that has all three of these indicators

from shared import create_or_update_dataset
import requests
import pandas
import os
import tempfile
import datetime
from edelweiss_data import QueryExpression as Q


def clean_dataframe(df, value_column_name):
    pivoted = df.melt(
        id_vars=["Country/Region", "Province/State", "Lat", "Long"], var_name="Date"
    )
    converted = pivoted.astype({"Date": "datetime64[ns]"})
    converted["Province/State"].fillna("", inplace=True)
    reindexed = converted.set_index(["Country/Region", "Province/State", "Date"])
    value_converted = reindexed.astype({"value": "int64"})
    value_converted.rename(columns={"value": value_column_name}, inplace=True)
    return value_converted


def download_and_clean(url, label):
    df = pandas.read_csv(url)
    return clean_dataframe(df, label)


sources = [
    {
        "url": r"https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv",
        "label": "Cases",
    },
    {
        "url": r"https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv",
        "label": "Deaths",
    },
    {
        "url": r"https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv",
        "label": "Recovered",
    },
]


def get_metadata(now, location):
    today = datetime.datetime.now()
    reporting_day = today
    # John Hopkins data is updated around 0:00 UCT but because it aggregates so much it's unclear when exactly the reporting interval ends
    estimated_reporting_cutoff = datetime.datetime(
        reporting_day.year,
        reporting_day.month,
        reporting_day.day,
        0,
        tzinfo=datetime.timezone.utc,
    )
    return {
        "datetimeRetrieved": "{}".format(now),
        "upstreamSource": location,
        "originalDataCollectionAgency": "https://systems.jhu.edu/",
        "dataBackgroundInformation": "https://github.com/CSSEGISandData/COVID-19",
        "estimatedReportingCutoff": "{}".format(estimated_reporting_cutoff),
        "category": "covid-19",
        "keywords": ["covid-19", "cases", "deaths", "by country"],
        "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
    }


def get_description(now, label, location):
    return """This dataset was created at {} and is updated daily around 1am GMT from [the original dataset by the Johns Hopkins University Center for Systems Science and Engineering]({})
which in turn sources the data from the World Health Organization, the China CDC and several other national institutions
([more information on the process](https://github.com/CSSEGISandData/COVID-19))

The upstream data release is split into several datasets which covers the numbers for COVID-19 cases, deaths and recovered cases in a wide format (timeseries with dates as columns). This dataset contains the numbers for the category "{}".

A derived and merged dataset in long form (one row per country/region and date containing the numbers for cases, deaths and recovered) is available in Edelweiss Data as well.

This data is made available in Edelweiss Data for easier consumption by the general public for educational purposes under a [CC BY-NC-SA license]("license": "https://creativecommons.org/licenses/by-nc-sa/4.0/")
    """.format(
        now, location, label
    )


def get_merged_description(now):
    return """This dataset was created at {} and is updated daily around 1am GMT from [several original dataset by the
Johns Hopkins University Center for Systems Science and Engineering](https://github.com/CSSEGISandData/COVID-19)
which in turn sources the data from the World Health Organization, the China CDC and several other national institutions
([more information on the process](https://github.com/CSSEGISandData/COVID-19))

The upstream data release is split into several datasets which covers the numbers for COVID-19 cases, deaths and recovered cases in a wide format (timeseries with dates as columns).
This dataset represents a merged dataset in long form (one row per country/region and date containing the numbers for cases, deaths and recovered).

This data is made available in Edelweiss Data for easier consumption by the general public for educational purposes under a [CC BY-NC-SA license]("license": "https://creativecommons.org/licenses/by-nc-sa/4.0/")
    """.format(
        now
    )


dataframes = [download_and_clean(**source) for source in sources]

dataframes_for_merging = [
    dataframes[0],
    dataframes[1].iloc[:, -1],
    dataframes[2].iloc[:, -1],
]  # dump the redundant lat/long columns for any but the first dataset
merged = pandas.concat(dataframes_for_merging, axis=1)

now = datetime.datetime.now(datetime.timezone.utc)


for source, data in zip(sources, dataframes):
    name = "COVID-19 dataset by John Hopkins University - {}".format(source["label"])
    metadata = get_metadata(now, source["url"])
    description = get_description(now, source["label"], source["url"])
    create_or_update_dataset(name, source["url"], metadata, description, data)

name = "COVID-19 dataset by John Hopkins University - Merged long form (cases, deaths, recovered)"
metadata = get_metadata(now, [source["url"] for source in sources])
description = get_merged_description(now)
create_or_update_dataset(name, source["url"], metadata, description, merged)
