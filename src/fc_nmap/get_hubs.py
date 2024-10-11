import os
import sys
from . GrpcClient import HubService
from grpc import FutureTimeoutError, RpcError, StatusCode
import time, datetime, random

from ipaddress import ip_address 

def get_hubs(hub_address, hubs):
	if not hub_address:
		print("No hub address. Check .env.sample")
		sys.exit(1)
	peers = None
	while not peers:
		try:
			hub = HubService(hub_address, use_async=False, timeout=5)
			peers = hub.GetCurrentPeers()
		except RpcError:
			hub_address = random.choice(list(hubs.keys()))
			time.sleep(1)

	
	for c in peers.contacts:
		if c.rpc_address.address != '127.0.0.1':
			id = f'{c.rpc_address.address}:{c.rpc_address.port}'
			if id not in hubs or hubs[id]['timestamp'] < c.timestamp:
				hubs[id] = {
					'family': c.rpc_address.family,
					'dns_name': c.rpc_address.dns_name,
					'hubv': c.hub_version,
					'appv': c.app_version,
					'timestamp': c.timestamp
					}
	hub.close()
	return hubs


def _get_hub_info(address, port, use_ssl=False, timeout=5):
	try:
		hub = HubService(f'{address}:{port}', use_async=False, timeout=timeout, use_ssl=use_ssl)
		info = hub.GetInfo(timeout=timeout)
		hub.close()
		return (None, info)
	except RpcError as e:
		return(e, None)

def get_hub_info(address, port, dnsname, timeout=5):
	if not ip_address(address).is_global:
		return None
	(error, info) = _get_hub_info(address, port, use_ssl=False, timeout=timeout)
	if error:
		if error.code() == StatusCode.DEADLINE_EXCEEDED:
			return
		if error.code() == StatusCode.UNAVAILABLE and dnsname.strip():
			(error,info) = _get_hub_info(dnsname, port, use_ssl=True)
			if not error:
				return info
			else:
				print(address, port, dnsname, error.code(), error.details())
				return None
				#sys.exit(1)
		else:
			return 
	else:
		return info