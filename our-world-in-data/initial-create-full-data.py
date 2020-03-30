import pandas
import datetime
from edelweiss_data import API

# location = r"https://covid.ourworldindata.org/data/ecdc/total_deaths.csv"
# df = pandas.read_csv(location)
# pivoted = df.melt(id_vars=['date'])
# pivoted.columns = ['date', 'country', 'deaths']
# reindexed = pivoted.set_index(['date', 'country'])
# cleaned = reindexed.dropna()
# converted = cleaned.astype({'deaths': 'int32'})
# converted.to_csv("test.csv")

location = r"https://covid.ourworldindata.org/data/ecdc/full_data.csv"
dataframe = pandas.read_csv(location)

now = datetime.now(timezone.utc)

metadata = {
    "datetimeRetrieved": "{}".format(now),
    "upstreamSource": location,
    "originalDataCollectionAgency": "https://www.ecdc.europa.eu/en/coronavirus",
    "dataBackgroundInformation": "https://ourworldindata.org/coronavirus-source-data",
    "category": "covid-19",
    "keywords": "covid-19; cases; deaths; by country",
}

description = """This dataset was created at {} created once daily around 6pm CET from [the original dataset by our world in data]({}) which in turn sources the data from the European Centre for Disease Prevention and Control (ECDC)
([more information on the process](https://ourworldindata.org/coronavirus-source-data)).
""".format(
    now, location
)


edelweiss_api_url = "https://api.develop.edelweiss.douglasconnect.com"
api = API(edelweiss_api_url)
api.authenticate(refresh_token=os.environ.get("REFRESH_TOKEN"))


dataset = api.create_in_progress_dataset(name)
try:
    dataset.upload_dataframe_data(dataframe)
    dataset.infer_schema()
    dataset.upload_metadata(metadata)
    dataset.set_description(description)
    published_dataset = dataset.publish("First import on {}".format(now))
    print("DATASET published:", published_dataset)
except requests.HTTPError as err:
    print("not published: ", err.response.text)
