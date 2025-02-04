# -*- coding: utf-8 -*-

from argparse import Namespace
from os.path import abspath, expanduser, expandvars

from mwclient import Site


class PageApp:
    def __init__(self, args: Namespace):
        assert isinstance(args.hostname, (type(None), str))
        assert isinstance(args.username, (type(None), str))
        assert isinstance(args.password, (type(None), str))
        assert isinstance(args.endpoint_path, str)
        assert isinstance(args.namespace, int)
        assert isinstance(args.all, bool)
        assert isinstance(args.pages, list)
        assert isinstance(args.cache_dir, str)

        if not args.hostname:
            raise ValueError("The 'hostname' argument is required")
        if not args.endpoint_path:
            raise ValueError("The 'endpoint_path' argument is required")
        if not args.cache_dir:
            raise ValueError("The 'hostname' argument is required")
        if args.namespace not in Site.default_namespaces:
            raise ValueError(f"Unexpected namespace number: {args.namespace}")

        self._hostname = args.hostname
        self._username = args.username
        self._password = args.password
        self._endpoint_path = args.endpoint_path
        self._namespace = args.namespace
        self._all = args.all
        self._pages = args.pages
        self._cache_dir = args.cache_dir

    @property
    def abs_cache_dir(self) -> str:
        return abspath(expanduser(expandvars(self._cache_dir)))

    def run(self) -> None:
        pass
