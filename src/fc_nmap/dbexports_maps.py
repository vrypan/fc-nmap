import folium
import sqlite3
import click

def get_latlong(dbpath="hubs.db", max_age=60*60*24):
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT count(*), addr.latitude, addr.longitude, addr.country_name, addr.city_name, addr.country_code
        FROM hub LEFT JOIN hub_info ,addr
        ON hub.ip = hub_info.ip AND hub.port = hub_info.port AND hub.ip = addr.ip
        WHERE unixepoch(hub.ts) > unixepoch() - ?
        GROUP BY latitude, longitude
        """, (max_age,))
    records = cursor.fetchall()
    return records

def create_map(dbpath="hubs.db", out='fc_nmap.html', max_age=60*60*24):
    hubs = get_latlong(dbpath, max_age)

    m = folium.Map(location=(20,15), zoom_start=3)
    radius = 5

    mean = sum([h[0] for h in hubs])/len(hubs)
    for h in hubs:
        if h[1]:
            folium.CircleMarker(
                location=[h[1], h[2]],
                radius=( (h[0]/mean)**(1./3.) )*10,
                color="#2E073F",
                weight=1,
                fill_opacity=0.6,
                opacity=1,
                fill_color="#7A1CAC",
                popup="{} meters".format(radius),
                tooltip=f"{h[0]} hub(s) in {h[4]}, {h[5]}",
            ).add_to(m)
    m.save(out)
    click.echo(f"Map saved to {out}")

