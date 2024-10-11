from fc_nmap import get_hubs

def test_hoyt():
    ret = get_hubs.get_hub_info('75.101.154.213', 2283, 'hoyt.farcaster.xyz')
    assert ret.nickname == 'hoyt'

"""
def test_kets():
    ret = get_hubs.get_hub_info('44.221.135.246', 2283, 'keats.merkle.zone')
    assert ret == None
"""

def test_local():
    ret = get_hubs.get_hub_info('10.0.0.1', 2283, '')
    assert ret == None