import yaml
from notion.client import NotionClient
from notion import block, collection
from datetime import datetime, timedelta

with open(r"secret.yml") as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    config = yaml.load(file, Loader=yaml.FullLoader)
    HABIT_LINK = config["HABIT_LINK"]
    NOTION_TOKEN = config["NOTION_TOKEN"]

client = NotionClient(token_v2=NOTION_TOKEN)

def get_today_row():
    pages = client.get_block(HABIT_LINK)
    today = datetime.today()
    today_str = today.strftime(format='%m/%d')
    rows = pages.collection.get_rows(search=today_str)
    if not rows:
        new_row = pages.collection.add_row()
        new_row.name = today_str
        new_row.date = collection.NotionDate(today.date())
        return new_row
    elif len(rows)>1:
        raise Exception("Seems your table has duplicate data")
    return rows[0]


def get_today_row_set():
    get_today_row()


def update_today_row_set(**kwarg):
    row = get_today_row()
    for k, v in kwarg.items():
        setattr(row, k, v)

get_today_row()
print("OK")
# update_today_row_set(music=True)