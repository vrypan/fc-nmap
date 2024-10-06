# SPDX-FileCopyrightText: 2024-present Panayotis Vryonis <vrypan@gmail.comm>
#
# SPDX-License-Identifier: MIT
import click
from datetime import datetime
import random

from fc_nmap.__about__ import __version__
from fc_nmap.get_hubs import get_hubs

@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="fc-nmap")
def fc_nmap():
    pass

@fc_nmap.command()
@click.option('--hub', default='', help='IP:port of hub to start crawling from.')
@click.option('--hops', default=20, help='Number of hubs to query.')
@click.option('--out', default='-', type=click.File('w'), help="Output file, leave empty for stdout")
def scan(hub, hops, out):
    """fc-nmap scan will scann the network starting from [HUB] and collect hub IPs, versions and last
    update timestamp.
    """
    hubs = {}
    with click.progressbar(
            length=hops, 
            label='Scanning', 
            width=0,
            show_eta=False,
            bar_template='%(label)s  %(bar)s  %(info)s',
            #fill_char='█',
            fill_char='#',
            item_show_func=lambda a: a.rjust(21) if a else None
        ) as bar:
        for i in range(hops):
            bar.update(1, hub)
            hubs = get_hubs(hub, hubs)
            hub = random.choice(list(hubs.keys()))
        bar.update(1,'Done.')
    for h in hubs:
        click.echo(f'{h}\t{hubs[h]['appv']}\t{datetime.fromtimestamp(int(hubs[h]['timestamp']/1000), tz=None)}', file=out)
    
    click.echo(f'Total hubs: {len(hubs)}')
