# SPDX-FileCopyrightText: 2024-present Panayotis Vryonis <vrypan@gmail.comm>
#
# SPDX-License-Identifier: MIT
import click
from datetime import datetime
import random
import sqlite3
import sys

from fc_nmap.__about__ import __version__
from fc_nmap.get_hubs import get_hubs, get_hub_info

@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="fc-nmap")
def fc_nmap():
    """Network Mapper for Farcaster
    """
    pass

@fc_nmap.command()
@click.option('--hub', default='', help='IP:port of hub to start crawling from.')
@click.option('--hops', default=20, help='Number of hubs to query.')
# @click.option('--out', default='-', type=click.File('w'), help="Output file, leave empty for stdout")
def scan(hub, hops):
    """fc-nmap scan will scann the network starting from [HUB] and collect hub IPs, versions and last
    update timestamp.
    """
    try:
        db_conn = sqlite3.connect('hubs.db')
        db_cursor = db_conn.cursor()
    except:
        click.echo('hubs.db not found. Run "fc-nmap initdb" to create it.')
        sys.exit(1)
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
        h_ip,h_port = h.split(':')
        h_app_ver   = hubs[h]['appv']
        h_proto_ver = hubs[h]['hubv']
        h_ts        = hubs[h]['timestamp']
        db_cursor.execute("""
            INSERT OR REPLACE INTO hub (ip, port, proto_version, app_version, ts) VALUES (?,?,?,?,?)
            """, 
            (h_ip, h_port, h_proto_ver, h_app_ver, h_ts)
        )
        # click.echo(f'{h}\t{hubs[h]['appv']}\t{datetime.fromtimestamp(int(hubs[h]['timestamp']/1000), tz=None)}', file=out)
    db_conn.commit()
    click.echo(f'Total hubs: {len(hubs)}')

@fc_nmap.command()
@click.argument('output', default='-', type=click.File('w'))
@click.option('--hub-info', is_flag=True, help="Collect hub info")
@click.option('--resolve', '-r',
              type=click.Choice(['city', 'country', 'latlong'], case_sensitive=False), multiple=True)
def updatedb(output, resolve, hub_info):
    """Collect addtional information about each hub
    """
    conn = sqlite3.connect('hubs.db')
    r_cursor = conn.cursor()
    w_cursor = conn.cursor()
    r_cursor.execute("""
        SELECT COUNT(*) FROM hub LEFT JOIN hub_info
        ON hub.ip = hub_info.ip AND hub.port = hub_info.port 
        WHERE unixepoch() - unixepoch(hub_info.updated_at) > 60*60*12
        OR hub_info.updated_at IS NULL
        """)
    count = r_cursor.fetchone()[0]

    # r_cursor.execute("""SELECT * FROM hub""")
    r_cursor.execute("""
        SELECT hub.ip, hub.port FROM hub LEFT JOIN hub_info
        ON hub.ip = hub_info.ip AND hub.port = hub_info.port 
        WHERE unixepoch() - unixepoch(hub_info.updated_at) > 60*60*12
        OR hub_info.updated_at IS NULL
        """)
    records = r_cursor.fetchall()

    i = 0
    with click.progressbar(records, 
        label=f"Scanning {count} hubs",
        length=count, 
        width=0, 
        bar_template='%(label)s  %(bar)s  %(info)s', 
        item_show_func=lambda a: a.rjust(21) if a else None
        ) as bar:
        for r in records:
            i+=1
            bar.update(1, f"{i}/{count}".rjust(10) )
            info = get_hub_info(f"{r[0]}:{r[1]}")
            if info:
                w_cursor.execute(
                    """
                    INSERT OR REPLACE INTO hub_info (ip, port, version, is_syncing, nickname, root_hash, peerid, fid) VALUES (?,?,?,?,?,?,?,?)
                    """,
                    (r[0],r[1], #ip:port
                    info.version,
                    info.is_syncing,
                    info.nickname,
                    info.root_hash,
                    info.peerId,
                    info.hub_operator_fid)
                    )
                conn.commit()
                line = f"{r[0]}:{r[1]} -- {info.hub_operator_fid}"
            else:
                w_cursor.execute(
                    """
                    INSERT OR REPLACE INTO hub_info (ip, port, fid) VALUES (?,?,?)
                    """,
                    (r[0],r[1], 0)
                )
                line = f"{r[0]}:{r[1]} -- Unknown".ljust(40)
            
            #print(line, f"{r[0]}:{r[1]}".ljust(30), end='\r', flush=True)
    conn.commit()
    
@fc_nmap.command()
def initdb():
    """Initialize the database"""
    conn = sqlite3.connect('hubs.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hub
        ( ip text, port integer, proto_version text, app_version text, ts timestamp )
    """)
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_hub_ip ON hub(ip, port)
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hub_info
        ( ip text, port INTEGER, 
            version TEXT, 
            is_syncing BOOL, 
            nickname TEXT, 
            root_hash TEXT, 
            peerid TEXT, 
            fid INTEGER, 
            updated_at TEXT NOT NULL DEFAULT current_timestamp
        )
    """)
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_hub_info_ip ON hub(ip, port)
    """)
    conn.commit()
    click.echo("hubs.db created.")
    
@fc_nmap.command()
@click.option('--out', default='-', type=click.File('w'), help="Output file, leave empty for stdout")
def dumpdb(out):
    """Create a tab separated dump of the database"""
    conn = sqlite3.connect('hubs.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT hub.ip, hub.port, hub.proto_version, hub.app_version, hub.ts, hub_info.fid
        FROM hub LEFT JOIN hub_info
        ON hub.ip = hub_info.ip AND hub.port = hub_info.port
        """)
    records = cursor.fetchall()
    for r in records:
        click.echo(f'{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\t{r[5]}\t{datetime.fromtimestamp(int(r[4]/1000), tz=None)}', file=out)

