import requests
import pandas
import os
import tempfile
import datetime
from edelweiss_data import QueryExpression as Q

url = "https://github.com/nytimes/covid-19-data/raw/master/us-states.csv"

def get_metadata(now):
    today = datetime.datetime.now()
    # It seems NYT data is updated around 14:00 UTC every day with data from the previous day but no hard information is available
    reporting_day = today - datetime.timedelta(days=1) if today.hour >= 15 else today - datetime.timedelta(days=2)
    estimated_reporting_cutoff = datetime.datetime(reporting_day.year, reporting_day.month, reporting_day.day, 20, tzinfo=datetime.timezone.utc)
    return { "datetimeRetrieved": "{}".format(now),
        "upstreamSource": url,
        "originalDataCollectionAgency": "https://www.nytimes.com",
        "dataBackgroundInformation": "https://github.com/nytimes/covid-19-data",
        "estimatedReportingCutoff": "{}".format(estimated_reporting_cutoff),
        "category": "covid-19",
        "keywords": ["covid-19", "cases", "deaths", "USA"],
        "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
    }

def get_description(now):
    return """This dataset was created at {}. It is updated once daily around 15:00 UTC from [the original dataset by the New York Times]({}) which gets the offial data once a day from the local health offices of the individual states.
([more information on the process](https://github.com/nytimes/covid-19-data)).

This data is made available in Edelweiss Data for easier consumption by the general public for educational purposes under a [CC BY-NC-SA license]("license": "https://creativecommons.org/licenses/by-nc-sa/4.0/"). If you use the data please make sure to
adhere to the license restrictions of the [New York Times](https://github.com/nytimes/covid-19-data/blob/master/LICENSE).
        """.format(
            now, url
        )


def get_data():
   df = pandas.read_csv(url)
   value_converted = df.astype({"date": "datetime64[ns]", "cases": "int64", "deaths": "int64"})
   return value_converted


def upload_data(api, now, dataset, dataframe):
    try:
        with tempfile.TemporaryFile(mode="w+") as temp:
            dataframe.to_csv(temp, line_terminator="\n", index=False)
            temp.seek(0)
            dataset.upload_data(temp)
        dataset.infer_schema()
        dataset.upload_metadata(get_metadata(now))
        dataset.set_description(get_description(now))
        published_dataset = dataset.publish("First import on {}".format(now))
    except requests.HTTPError as err:
        print("not published: ", err.response.text)


def create_initial_dataset(api, name, now, dataframe):
    dataset = api.create_in_progress_dataset(name)
    upload_data(api, now, dataset, dataframe)


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
    upload_data(api, now, dataset, dataframe)
