import pandas
import tempfile
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


def create_metadata(now, location):
    return {
        "datetimeRetrieved": "{}".format(now),
        "upstreamSource": location,
        "originalDataCollectionAgency": "https://systems.jhu.edu/",
        "dataBackgroundInformation": "https://github.com/CSSEGISandData/COVID-19",
        "category": "covid-19",
        "keywords": ["covid-19", "cases", "deaths", "by country"],
    }


def create_description(now, label, location):
    return """This dataset was created at {} and is updated daily around 1am GMT from [the original dataset by the Johns Hopkins University Center for Systems Science and Engineering]({})
which in turn sources the data from the World Health Organization, the China CDC and several other national institutions
([more information on the process](https://github.com/CSSEGISandData/COVID-19))

The upstream data release is split into several datasets which covers the numbers for COVID-19 cases, deaths and recovered cases in a wide format (timeseries with dates as columns). This dataset contains the numbers for the category "{}".

A derived and merged dataset in long form (one row per country/region and date containing the numbers for cases, deaths and recovered) is available in Edelweiss Data as well.
    """.format(
        now, location, label
    )


def create_merged_description(now):
    return """This dataset was created at {} and is updated daily around 1am GMT from [several original dataset by the
Johns Hopkins University Center for Systems Science and Engineering](https://github.com/CSSEGISandData/COVID-19)
which in turn sources the data from the World Health Organization, the China CDC and several other national institutions
([more information on the process](https://github.com/CSSEGISandData/COVID-19))

The upstream data release is split into several datasets which covers the numbers for COVID-19 cases, deaths and recovered cases in a wide format (timeseries with dates as columns).
This dataset represents a merged dataset in long form (one row per country/region and date containing the numbers for cases, deaths and recovered).
    """.format(
        now
    )


def upload_data(api, now, source, dataframe, dataset, description=None):
    try:
        with tempfile.TemporaryFile(mode="w+") as temp:
            dataframe.to_csv(temp, line_terminator="\n")
            temp.seek(0)
            dataset.upload_data(temp)
        dataset.infer_schema()
        dataset.upload_metadata(create_metadata(now, source["url"]))
        if description is None:
            description = create_description(now, source["label"], source["url"])
        dataset.set_description(description)
        published_dataset = dataset.publish("First import on {}".format(now))
    except requests.HTTPError as err:
        print("not published: ", err.response.text)


def upload_dataset(api, now, source, dataframe, description=None):
    dataset = api.create_in_progress_dataset("COVID-19 dataset by John Hopkins University - {}".format(source["label"]))
    upload_data(api, now, source, dataframe, dataset, description)


def update_dataset(api, now, source, dataframe, description=None):
    datasetname = "COVID-19 dataset by John Hopkins University - {}".format(source["label"])
    datasets_filter = Q.exact_search(Q.system_column("name"), datasetname)
    datasets = api.get_published_datasets(condition=datasets_filter)
    if datasets.shape[1] != 1:
        raise Exception("Did not get exactly one dataset named {}".format(datasetname))
    published_dataset = datasets.iloc[0, -1]
    dataset = published_dataset.new_version()
    upload_data(api, now, source, dataframe, dataset, description)
