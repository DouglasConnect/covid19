import pandas
from datetime import datetime, timezone
from edelweiss_data import API
import requests
import os

now = datetime.now(timezone.utc)

location = r"https://covid.ourworldindata.org/data/ecdc/full_data.csv"
dataframe = pandas.read_csv(location)

metadata = {
    "datetimeRetrieved": "{}".format(now),
    "upstreamSource": location,
    "originalDataCollectionAgency": "https://www.ecdc.europa.eu/en/coronavirus",
    "dataBackgroundInformation": "https://ourworldindata.org/coronavirus-source-data",
    "category": "covid-19",
    "keywords": ["covid-19", "cases", "deaths", "by country"],
}

description = """This dataset was created at {} created once daily around 6pm CET from [the original dataset by our world in data]({}) which in turn sources the data from the European Centre for Disease Prevention and Control (ECDC)
([more information on the process](https://ourworldindata.org/coronavirus-source-data)).
""".format(
    now, location
)


edelweiss_api_url = "https://api.develop.edelweiss.douglasconnect.com"
api = API(edelweiss_api_url)
api.authenticate(refresh_token=os.environ.get("REFRESH_TOKEN"))


published_dataset = api.get_published_dataset("e06e9223-5e5d-42c2-a090-feba0bcee19a")
dataset = published_dataset.new_version()
try:
    dataset.upload_dataframe_data(dataframe)
    dataset.infer_schema()
    dataset.upload_metadata(metadata)
    dataset.set_description(description)
    published_dataset = dataset.publish("Update of data at {}".format(now))
    print("DATASET published:", published_dataset)
except requests.HTTPError as err:
    print("not published: ", err.response.text)
