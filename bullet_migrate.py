from datetime import datetime, timedelta
from calendar import day_name
from typing import Callable
import yaml
from notion.client import NotionClient
from notion import block

with open(r'secret.yml') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    config = yaml.load(file, Loader=yaml.FullLoader)
    PAGE_LINK = config['PAGE_LINK']
    NOTION_TOKEN = config['NOTION_TOKEN']

today = datetime.today()

client = NotionClient(token_v2=NOTION_TOKEN)
# Replace this URL with the URL of the page you want to edit
pages = client.get_block(PAGE_LINK)


def _get_next_monday(day):
    while day.weekday() != 0:
        day += timedelta(days=1)
    return day


def recursive_find(node, filter: Callable, all=False):
    result = []
    node_list = [node]
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


def get_element(content, element_name, node, finder: Callable):
    if not content.get(element_name) and (
            result := recursive_find(node, finder)):
        return result


content = {}
month_list = []
# fetch the data
for i, page in enumerate(pages.children):
    if not content.get('template') and (
        result := recursive_find(page, lambda r: getattr(
            r, 'title', None) == 'Empty Week Template')):
        content.setdefault('template', result)

    if getattr(page, 'title', None) == 'Weekly Journal':
        for p in pages.children[i+1: i+7]:
            month_list += p.children
        content.setdefault('month_list', month_list)
        break

for i, page in enumerate(content['month_list']):
    if not content.get('current_week') and (
        result := recursive_find(
            page, lambda r: getattr(r, 'icon', None) == '🚀')):
        content.setdefault('current_week', result)
    if not content.get('next_week') and (
        result := recursive_find(
            page, lambda r: getattr(r, 'icon', None) == '🌎')):
        content.setdefault('next_week', result)


# current -> past
content['current_week'].icon = '🌕'
unfinished_tasks = recursive_find(content['current_week'], lambda r: getattr(
    r, 'checked', None) == False, all=True)

# future -> current
content['next_week'].icon = '🚀'
for task in unfinished_tasks:
    task.move_to(content['next_week'])
    task.title = '\>' + task.title

# create new future
first_day: datetime = _get_next_monday(today) + timedelta(days=7)
new_week = content['month_list'][-first_day.month].children.add_new(
    block.PageBlock, title=f"{first_day.strftime('%m%d')}-{(first_day+timedelta(days=6)).strftime('%m%d')}")
new_week.children.add_new(block.BreadcrumbBlock)
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
        block.SubheaderBlock, title=f"{day_name[i][:3]} {(first_day + timedelta(days=i)).day}",
        color='orange_background')
weekend_block = new_week.children.add_new(block.ColumnListBlock)
for i in range(5, 7):
    _day_block = weekend_block.children.add_new(block.ColumnBlock)
    _day_block.children.add_new(
        block.SubheaderBlock, title=f"{day_name[i][:3]} {(first_day + timedelta(days=i)).day}",
        color='blue_background')
new_week.children.add_new(block.DividerBlock)
new_week.children.add_new(block.DividerBlock)
new_week.children.add_new(block.HeaderBlock, title="Weekly Inbox")
new_week.icon = '🌎'
print("have fun")
