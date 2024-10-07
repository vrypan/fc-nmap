import os
import sys
from farcaster.HubService import HubService
import time, datetime, random

def get_hubs(hub_address, hubs):
	if not hub_address:
		print("No hub address. Check .env.sample")
		sys.exit(1)
	peers = None
	while not peers:
		try:
			hub = HubService(hub_address, use_async=False)
			peers = hub.GetCurrentPeers()
		except:
			# print(f"=== {hub_address} did not respond")
			# print(f'=== {hub_address}\t{hubs[hub_address]['appv']}\t{datetime.datetime.fromtimestamp(int(hubs[hub_address]['timestamp']/1000), tz=None)}')
			hub_address = random.choice(list(hubs.keys()))
			time.sleep(1)

	
	for c in peers.contacts:
		if c.rpc_address.address != '127.0.0.1':
			# print(c)
			id = f'{c.rpc_address.address}:{c.rpc_address.port}'
			if id not in hubs:
				# print(f'n {id}\t{c.app_version}\t\t{datetime.datetime.fromtimestamp(int(c.timestamp/1000), tz=None)}')
				hubs[id] = {
					'hubv': c.hub_version,
					'appv': c.app_version,
					'timestamp': c.timestamp
					}

			if id in hubs and hubs[id]['timestamp'] < c.timestamp:
				# if hubs[id]['appv'] != c.app_version:
				#	print(f'u {id}\t{c.app_version}({hubs[id]['appv']})\t{datetime.datetime.fromtimestamp(int(c.timestamp/1000), tz=None)}')
				#else:
				#	print(f't {id}\t{c.app_version}({hubs[id]['appv']})\t{datetime.datetime.fromtimestamp(int(c.timestamp/1000), tz=None)}\t{datetime.datetime.fromtimestamp(int(hubs[id]['timestamp']/1000), tz=None)}')

				hubs[id] = {
					'hubv': c.hub_version,
					'appv': c.app_version,
					'timestamp': c.timestamp
					}
			#	print(f't {id}\t{c.app_version}\t\t{datetime.datetime.fromtimestamp(int(c.timestamp/1000), tz=None)}')

			
	# print('=== Last Hub queried: ', hub_address )
	# print('=== Total hubs: ', len(hubs) )
	
	# print('=== Next Hub to be queried: ', hub_address )
	# print()
	hub.close()
	return hubs

def get_hub_info(hub_address):
	try:
		hub = HubService(hub_address, use_async=False)
		info = hub.GetInfo()
		hub.close()
		return info
	except:
		return None
