import pandas
import datetime
from edelweiss_data import API
import os
from shared import *

dataframes = [download_and_clean(**source) for source in sources]

dataframes_for_merging = [
    dataframes[0],
    dataframes[1].iloc[:, -1],
    dataframes[2].iloc[:, -1],
]  # dump the redundant lat/long columns for any but the first dataset
merged = pandas.concat(dataframes_for_merging, axis=1)

now = datetime.datetime.now(datetime.timezone.utc)

edelweiss_api_url = "https://api.develop.edelweiss.douglasconnect.com"
api = API(edelweiss_api_url)
api.authenticate(refresh_token=os.environ.get("REFRESH_TOKEN"))

for source, dataframe in zip(sources, dataframes):
    update_dataset(api, now, source, dataframe)

update_dataset(
    api,
    now,
    {
        "url": [ source["url"] for source in sources ],
        "label": "Merged long form (cases, deaths, recovered)",
    },
    merged,
    create_merged_description(now),
)
