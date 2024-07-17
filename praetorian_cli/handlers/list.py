import io
import json
from contextlib import redirect_stdout

import click

from praetorian_cli.handlers.chariot import chariot
from praetorian_cli.handlers.cli_decorators import cli_handler, list_options, page_options, plugins
from praetorian_cli.handlers.utils import key_set, paginate, display_list


@chariot.group()
@cli_handler
def list(ctx):
    """Get a list of resources from Chariot"""
    pass


list_filter = {'jobs': 'updated', 'files': 'name', 'accounts': 'name', 'integrations': 'name', 'definitions': 'name',
               'attributes': 'name'}


def attribute_filter(controller, key, offset, details, page):
    f = io.StringIO()
    with redirect_stdout(f):
        paginate(controller, key, 'attributes', "", offset, True, page)
    attr_output = json.loads(f.getvalue())
    output = {"data": [controller.my(dict(key=hit["source"])) for hit in attr_output["data"]]} if details else None
    if details:
        display_list(output, details)
    else:
        for hit in attr_output["data"]:
            click.echo(hit["source"])


@list.command('assets')
@click.option('-attr', '--attribute', nargs=2, help='Filter by attribute name and value')
@list_options('DNS')
@page_options
def assets(controller, filter, offset, details, page, attr):
    """List assets"""
    if attr:
        attribute_filter(controller, f'#attribute#{attr[0]}#{attr[1]}#asset#{filter}', offset, details, page)
        return

    paginate(controller, f'#asset#{filter}', 'assets', "", offset, details, page)


@list.command('risks')
@list_options('name')
@page_options
@click.option('-attr', '--attribute', nargs=2, help='Filter by attribute name and value')
def risks(controller, filter, offset, details, page, attr):
    """List risks"""
    if attr:
        attribute_filter(controller, f'#attribute#{attr[0]}#{attr[1]}#risk#{filter}', details)
        return

    paginate(controller, f'#risk#{filter}', 'risks', "", offset, details, page)


def create_list_command(item_type, item_filter):
    @list.command(item_type, help=f"List {item_type}")
    @list_options(item_filter)
    @page_options
    @plugins
    def command(controller, filter, offset, details, page):
        if item_type == 'accounts' or item_type == 'integrations':
            paginate(controller, f'{key_set[item_type]}', item_type, filter, offset, details, page)
        else:
            paginate(controller, f'{key_set[item_type]}{filter}', item_type, "", offset, details, page)


for key, value in list_filter.items():
    create_list_command(key, value)
