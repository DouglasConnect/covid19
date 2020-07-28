import os
import tempfile
import datetime
import requests
from edelweiss_data import API, QueryExpression as Q


def dataset_exists(api, name):
    """ Check if a dataset with this name already exists """
    datasets_filter = Q.exact_search(Q.system_column("name"), name)
    datasets = api.get_published_datasets(condition=datasets_filter)
    return not datasets.empty


def upload_data_and_publish(api, dataset, dataframe, metadata, description, changelog):
    """ Upload a given pandas dataframe, metadata and description and publish (a new version of) a dataset """
    try:
        with tempfile.TemporaryFile(mode="w+") as temp:
            dataframe.to_csv(temp, line_terminator="\n", index=True)
            temp.seek(0)
            dataset.upload_data(temp)
        dataset.infer_schema()
        dataset.upload_metadata(metadata)
        dataset.set_description(description)
        dataset.publish(changelog)
    except requests.HTTPError as err:
        print("Error updating dataset: ", err.response.text)


def create_initial_dataset(api, name, dataframe, metadata, description):
    """ Create the initial version of a dataset """
    dataset = api.create_in_progress_dataset(name)
    upload_data_and_publish(api, dataset, dataframe, metadata, description, "Initial import of data at {}".format(datetime.datetime.now()))


def update_dataset(api, name, dataframe, metadata, description):
    """ Update an existing dataset """
    datasets_filter = Q.exact_search(Q.system_column("name"), name)
    datasets = api.get_published_datasets(condition=datasets_filter)
    if datasets.shape[1] != 1:
        raise Exception("Did not get exactly one dataset named {}".format(name))
    published_dataset = datasets.iloc[0, -1]
    try:
        in_progress = api.get_in_progress_dataset(published_dataset.id)
        in_progress.delete()
    except Exception:
        pass
    dataset = published_dataset.new_version()
    upload_data_and_publish(api, dataset, dataframe, metadata, description, "Daily update of data at {}".format(datetime.datetime.now()))


def create_or_update_dataset(name, url, metadata, description, data):
    """ Create or update a dataset with a given name """
    edelweiss_api_url = "https://api.edelweissdata.com"
    api = API(edelweiss_api_url)
    api.authenticate(refresh_token=os.environ.get("REFRESH_TOKEN"), scopes=['exceedQuota'])

    name = name
    if dataset_exists(api, name):
        update_dataset(api, name, data, metadata, description)
    else:
        create_initial_dataset(api, name, data, metadata, description)
