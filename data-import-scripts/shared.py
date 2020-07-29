import os
import tempfile
import datetime
from pandas import DataFrame
from typing import Optional, Dict
from edelweiss_data.api import InProgressDataset
import numpy
from edelweiss_data import API, InProgressDataset, QueryExpression as Q
from slack_webhook import Slack

def dataset_exists(api: API, name: str):
    """ Check if a dataset with this name already exists """
    datasets_filter = Q.exact_search(Q.system_column("name"), name)
    datasets = api.get_published_datasets(condition=datasets_filter)
    return not datasets.empty


def upload_data_and_publish(api: API, dataset: InProgressDataset, dataframe : DataFrame, metadata: dict, description: str, column_descriptions: Optional[Dict[str, str]], changelog: str):
    """ Upload a given pandas dataframe, metadata and description and publish (a new version of) a dataset """
    with tempfile.TemporaryFile(mode="w+") as temp:
        dataframe.to_csv(temp, line_terminator="\n", index=True)
        temp.seek(0)
        dataset.upload_data(temp)
    dataset.infer_schema()
    if column_descriptions is not None:
        for column in dataset.schema.columns:
            column.description = column_descriptions.get(column.name, "")
        dataset.update(schema=dataset.schema)
    dataset.upload_metadata(metadata)
    dataset.set_description(description)
    dataset.publish(changelog)


def create_initial_dataset(api: API, name: str, dataframe: DataFrame, metadata: dict, description: str, column_descriptions: Optional[Dict[str, str]]):
    """ Create the initial version of a dataset """
    dataset = api.create_in_progress_dataset(name)
    upload_data_and_publish(
        api, dataset, dataframe, metadata, description, column_descriptions, "Initial import of data at {}".format(datetime.datetime.now())
    )


def update_dataset(api: API, name: str, dataframe: DataFrame, metadata: dict, description: str, column_descriptions: Optional[Dict[str, str]]):
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
    upload_data_and_publish(api, dataset, dataframe, metadata, description, column_descriptions, "Daily update of data at {}".format(datetime.datetime.now()))


def create_or_update_dataset(name: str, metadata: dict, description: str, data: DataFrame, column_descriptions: Optional[Dict[str, str]]=None):
    """ Create or update a dataset with a given name """
    try:
        edelweiss_api_url = "https://api.edelweissdata.com"
        api = API(edelweiss_api_url)
        api.authenticate(refresh_token=os.environ.get("REFRESH_TOKEN"))

        name = name
        if dataset_exists(api, name):
            update_dataset(api, name, data, metadata, description, column_descriptions)
        else:
            create_initial_dataset(api, name, data, metadata, description, column_descriptions)
    except Exception as e:
        # Try to notify us via slack
        slack = Slack(url=os.environ.get("SLACK_HOOK"))
        message = f"Importing {name} failed with error: {e}"
        slack.post(text=message)
        raise # re-raise so the action is registered as failed
