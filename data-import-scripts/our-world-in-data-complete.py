from shared import create_or_update_dataset
import requests
import pandas
import os
import tempfile
import datetime
from edelweiss_data import QueryExpression as Q

name = "COVID-19 complete dataset by Our World In Data"
url = r"https://covid.ourworldindata.org/data/owid-covid-data.csv"


def get_metadata(now):
    today = datetime.datetime.now()
    # Our world in data mainly uses data that is reported and compiled until 10 CEST -> 8 UTC but there is some delay until publishing
    reporting_day = today if today.hour >= 18 else today - datetime.timedelta(days=1)
    estimated_reporting_cutoff = datetime.datetime(
        reporting_day.year,
        reporting_day.month,
        reporting_day.day,
        8,
        tzinfo=datetime.timezone.utc,
    )
    return {
        "datetimeRetrieved": "{}".format(now),
        "upstreamSource": url,
        "originalDataCollectionAgency": "https://www.ecdc.europa.eu/en/coronavirus",
        "dataBackgroundInformation": "https://ourworldindata.org/coronavirus-source-data",
        "estimatedReportingCutoff": "{}".format(estimated_reporting_cutoff),
        "category": "covid-19",
        "keywords": ["covid-19", "cases", "deaths", "by country", "testing"],
        "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
    }


def get_description(now):
    return """This dataset was created at {} created once daily around 6pm CET from [the original dataset by our world in data]({}) which in turn sources the data from the European Centre for Disease Prevention and Control (ECDC)
([more information on the process](https://ourworldindata.org/coronavirus-source-data)).

This data is made available in Edelweiss Data for easier consumption by the general public for educational purposes under a [CC BY-NC-SA license]("license": "https://creativecommons.org/licenses/by-nc-sa/4.0/")
        """.format(
        now, url
    )


def get_data():
    dataframe = pandas.read_csv(url)
    return dataframe


now = datetime.datetime.now(datetime.timezone.utc)
metadata = get_metadata(now)
description = get_description(now)
data = get_data()
create_or_update_dataset(name, url, metadata, description, data)
