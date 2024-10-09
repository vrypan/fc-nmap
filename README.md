# fc-nmap

**THis software is still in alpha and under heavy development.** Things will change and break.

[![PyPI - Version](https://img.shields.io/pypi/v/fc-nmap.svg)](https://pypi.org/project/fc-nmap)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fc-nmap.svg)](https://pypi.org/project/fc-nmap)

-----

## Usage

```console
pip install fc-nmap

fc-nmap --help

Usage: fc-nmap [OPTIONS] COMMAND [ARGS]...

  Farcaster Network Mapper

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  dumpdb    Create a tab separated dump of the database
  initdb    Initialize the database
  scan      fc-nmap scan will scann the network starting from [HUB] and...
  updatedb  Collect addtional information about each hub
```

`scan` will start from one hub, get its contact list and ask other hubs for their lists. Based on my tests so far, `hops > 10` will make litte difference.
Data collected is stored in a local sqlite3 db.

`updatedb` will collect additiona info. 

`dumpdb` generates a text export.

## License

`fc-nmap` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
