import pandas
from datetime import datetime, timezone
from edelweiss_data import API
from shared import *

df = get_data()
now = datetime.now(datetime.timezone.utc)

edelweiss_api_url = "https://api.develop.edelweiss.douglasconnect.com"
api = API(edelweiss_api_url)
api.authenticate(refresh_token=os.environ.get("REFRESH_TOKEN"))

name = "COVID-19 data for Germany by state (RKI data)"
create_initial_dataset(api, name, now, df)
