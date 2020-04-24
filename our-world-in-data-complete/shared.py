import requests
import pandas
import os
import tempfile
import datetime
import numpy
from edelweiss_data import QueryExpression as Q

url = r"https://covid.ourworldindata.org/data/owid-covid-data.csv"
df = pandas.read_csv(url)

def get_metadata(now):
    today = datetime.datetime.now()
    # Our world in data mainly uses data that is reported and compiled until 10 CEST -> 8 UTC but there is some delay until publishing
    reporting_day = today if today.hour >= 18 else today - datetime.timedelta(days=1)
    estimated_reporting_cutoff = datetime.datetime(reporting_day.year, reporting_day.month, reporting_day.day, 8, tzinfo=datetime.timezone.utc)
    return { "datetimeRetrieved": "{}".format(now),
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


def upload_data(api, now, dataset, dataframe, changelog):
    try:
        with tempfile.TemporaryFile(mode="w+") as temp:
            dataframe.to_csv(temp, line_terminator="\n", index=True)
            temp.seek(0)
            dataset.upload_data(temp)
        dataset.infer_schema()
        dataset.upload_metadata(get_metadata(now))
        dataset.set_description(get_description(now))
        published_dataset = dataset.publish(changelog)
    except requests.HTTPError as err:
        print("not published: ", err.response.text)


def create_initial_dataset(api, name, now, dataframe):
    dataset = api.create_in_progress_dataset(name)
    upload_data(api, now, dataset, dataframe, "Initial import of data at {}".format(now))


def update_dataset(api, name, now, dataframe):
    datasets_filter = Q.exact_search(Q.system_column("name"), name)
    datasets = api.get_published_datasets(condition=datasets_filter)
    if datasets.shape[1] != 1:
        raise Exception("Did not get exactly one dataset named {}".format(datasetname))
    published_dataset = datasets.iloc[0, -1]
    try:
        in_progress = api.get_in_progress_dataset(published_dataset.id)
        in_progress.delete()
    except:
        pass
    dataset = published_dataset.new_version()
    upload_data(api, now, dataset, dataframe, "Daily update of data at {}".format(now))
