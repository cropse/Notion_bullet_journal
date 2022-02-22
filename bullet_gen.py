from calendar import day_name
from datetime import datetime, timedelta
from typing import Callable

from copy import copy
import yaml
from notion import block, collection
from notion.client import NotionClient


def _get_next_monday(day: datetime) -> datetime:
    """
    Get closed monday according your date
    """
    while day.weekday() != 0:
        # Before Friday, probably just forgot so go to past Mon.
        if day.weekday() <= 4:
            day -= timedelta(days=1)
        else:
            day += timedelta(days=1)
    return day


def deep_find(node, filter: Callable, all=False):
    """
    Find the node acoording to filter.
    Set `all` = True to get all node instead of first.
    """
    result = []
    node_list = copy(node) if isinstance(node, list) else [node]
    while node_list:
        r = node_list.pop()
        if filter(r):
            if not all:
                return r
            else:
                result.append(r)
        elif r.children:
            node_list += r.children
    return result if all else None


with open(r"secret.yml") as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    config = yaml.load(file, Loader=yaml.FullLoader)
    PAGE_LINK = config["PAGE_LINK"]
    NOTION_TOKEN = config["NOTION_TOKEN"]
    ROUTINE = config["ROUTINE"]

today = datetime.today()

client = NotionClient(token_v2=NOTION_TOKEN)
# Replace this URL with the URL of the page you want to edit
pages = client.get_block(PAGE_LINK)

content = {}
month_list = []
# fetch the data
for i, page in enumerate(pages.children):
    if getattr(page, "title", None) == "Weekly Journal":
        # expand each ColumnListBlock to month_list
        for p in pages.children[i + 1:i + 7]:
            month_list += p.children
        content.setdefault("month_list", month_list)
        break

rocket = deep_find(content["month_list"],
    lambda r: getattr(r, "icon", None) == "🚀")
content.setdefault("current_week", rocket)

earth = deep_find(content["month_list"],
    lambda r: getattr(r, "icon", None) == "🌎")
content.setdefault("next_week", earth)

# create new future
print("Let's create new future")
first_day: datetime = _get_next_monday(today) + timedelta(days=7)
future_title = (
    f"{first_day.strftime('%m%d')}-{(first_day+timedelta(days=6)).strftime('%m%d')}"
)

if content["next_week"].title == future_title:
    print("Seems you already created future task right?")
    raise Exception("Seems you already created future task right?")

# create brand new future task
new_week = content["month_list"][-first_day.month].children.add_new(
    block.PageBlock, title=future_title)
# new_week.children.add_new(block.BreadcrumbBlock)
new_week.children.add_new(block.DividerBlock)
main_block = new_week.children.add_new(block.ColumnListBlock)
main_block.children.add_new(block.ColumnBlock).children.add_new(
    block.HeaderBlock, title="Weekly Goals")
main_block.children.add_new(block.ColumnBlock).children.add_new(
    block.HeaderBlock, title="Weekly Note")
new_week.children.add_new(block.DividerBlock)
weekdays_block = new_week.children.add_new(block.ColumnListBlock)
for i in range(5):
    _day_block = weekdays_block.children.add_new(block.ColumnBlock)
    _day_block.children.add_new(
        block.SubheaderBlock,
        title=f"{day_name[i][:3]} {(first_day + timedelta(days=i)).day}",
        color="orange_background",
    )
weekend_block = new_week.children.add_new(block.ColumnListBlock)
for i in range(5, 7):
    _day_block = weekend_block.children.add_new(block.ColumnBlock)
    _day_block.children.add_new(
        block.SubheaderBlock,
        title=f"{day_name[i][:3]} {(first_day + timedelta(days=i)).day}",
        color="blue_background",
    )
new_week.children.add_new(block.DividerBlock)
new_week.children.add_new(block.DividerBlock)
new_week.children.add_new(block.HeaderBlock, title="Weekly Inbox")
# add routine in future task
for r in ROUTINE:
    new_week.children.add_new(block.TodoBlock, title=r, color="blue")

new_week.icon = "🌎"
new_week.set('format.page_full_width', True)  # full width for desktop

# current -> past
content["current_week"].icon = "🌕"
unfinished_tasks = deep_find(  # Todo task
    content["current_week"],
    lambda r: (isinstance(r, block.TodoBlock) and getattr(
        r, "checked", None) == False) and
        not isinstance(r.parent, collection.CollectionRowBlock),
    all=True)

unfinished_page_tasks = deep_find(  # Page link task
    content["current_week"],
    lambda r: (isinstance(r, collection.CollectionRowBlock) and getattr(
        r, "done", None) == False),
    all=True,
)

# future -> current
content["next_week"].icon = "🚀"
for task in unfinished_tasks:
    task.move_to(content["next_week"])
    task.title = "\>" + task.title

for task in set(unfinished_page_tasks):
    content["next_week"].children.add_alias(task)

print("have fun")
