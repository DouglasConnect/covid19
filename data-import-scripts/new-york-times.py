from shared import create_or_update_dataset
import pandas
import datetime
from edelweiss_data import QueryExpression as Q

name = "COVID-19 data for the USA by state (New York Times data)"
url = "https://github.com/nytimes/covid-19-data/raw/master/us-states.csv"


def get_metadata(now, regions):
    today = datetime.datetime.now()
    # It seems NYT data is updated around 14:00 UTC every day with data from the previous day but no hard information is available
    reporting_day = (
        today - datetime.timedelta(days=1)
        if today.hour >= 15
        else today - datetime.timedelta(days=2)
    )
    estimated_reporting_cutoff = datetime.datetime(
        reporting_day.year,
        reporting_day.month,
        reporting_day.day,
        20,
        tzinfo=datetime.timezone.utc,
    )
    return {
        "datetimeRetrieved": "{}".format(now),
        "upstreamSource": url,
        "originalDataCollectionAgency": "https://www.nytimes.com",
        "dataBackgroundInformation": "https://github.com/nytimes/covid-19-data",
        "estimatedReportingCutoff": "{}".format(estimated_reporting_cutoff),
        "category": "covid-19",
        "keywords": ["covid-19", "cases", "deaths", "USA"],
        "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "columnNames": {
            "region": "state",
            "date": "date",
            "total-cases": "cases",
            "total-deaths": "deaths",
        },
        "regions": regions,
    }


def get_description(now):
    return """# COVID-19 data for the USA
### State level data as aggregated and published by the New York Times

This dataset was created at {}. It is updated once daily around 15:00 UTC from [the original dataset by the New York Times]({}) which gets the offial data once a day from the local health offices of the individual states.
([more information on the process](https://github.com/nytimes/covid-19-data)).

This data is made available in Edelweiss Data for easier consumption by the general public for educational purposes under a [CC BY-NC-SA license]("license": "https://creativecommons.org/licenses/by-nc-sa/4.0/"). If you use the data please make sure to
adhere to the license restrictions of the [New York Times](https://github.com/nytimes/covid-19-data/blob/master/LICENSE).
        """.format(
        now, url
    )


def get_data():
    df = pandas.read_csv(url)
    value_converted = df.astype(
        {"date": "datetime64[ns]", "cases": "int64", "deaths": "int64"}
    )
    return value_converted


now = datetime.datetime.now(datetime.timezone.utc)
description = get_description(now)
data = get_data()
metadata = get_metadata(now, [ l for l in data.loc[:,"state"].unique() ])
create_or_update_dataset(name, url, metadata, description, data)
