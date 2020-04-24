import pandas
import datetime
from edelweiss_data import API
from shared import *

df = get_data()
now = datetime.datetime.now(datetime.timezone.utc)

edelweiss_api_url = "https://api.develop.edelweiss.douglasconnect.com"
api = API(edelweiss_api_url)
api.authenticate(refresh_token=os.environ.get("REFRESH_TOKEN"))

name = "COVID-19 complete dataset by Our World In Data"
create_initial_dataset(api, name, now, df)
