# -*- coding: utf-8 -*-

import os
from argparse import Namespace
from pathlib import Path
from typing import Optional, Sequence, Tuple

from mwclient import Site
from mwclient.image import Image

from mwfilter.logging.logging import logger
from mwfilter.mw.cache_dirs import pages_cache_dirpath
from mwfilter.mw.image_list import ImageList


class ImageApp:
    def __init__(self, args: Namespace):
        assert isinstance(args.hostname, str)
        assert isinstance(args.cache_dir, str)
        assert args.hostname
        assert os.path.isdir(args.cache_dir)

        # Common arguments
        assert isinstance(args.yes, bool)
        assert isinstance(args.ignore_errors, bool)

        # Subparser arguments
        assert isinstance(args.endpoint_path, str)
        assert isinstance(args.username, (type(None), str))
        assert isinstance(args.password, (type(None), str))
        assert isinstance(args.image_page, str)
        assert isinstance(args.output_dir, str)
        assert isinstance(args.stdout, bool)

        self._hostname = args.hostname
        self._yes = args.yes
        self._ignore_errors = args.ignore_errors
        self._endpoint_path = args.endpoint_path
        self._username = args.username
        self._password = args.password
        self._image_page = args.image_page
        self._output_dir = Path(args.output_dir)
        self._stdout = args.stdout
        self._pages_dir = pages_cache_dirpath(args.cache_dir, self._hostname)

    @property
    def auth(self) -> Optional[Tuple[str, str]]:
        if self._username and self._password:
            return self._username, self._password
        else:
            return None

    def create_site(self) -> Site:
        site = Site(host=self._hostname, path=self._endpoint_path)
        if auth := self.auth:
            site.login(*auth)
        return site

    def read_image_list(self) -> ImageList:
        wiki_path = self._pages_dir / f"{self._image_page}.wiki"
        if not wiki_path.is_file():
            raise FileNotFoundError(f"File not found: '{str(wiki_path)}'")

        logger.debug(f"Read image list wiki file: '{wiki_path}'")
        mediawiki_content = wiki_path.read_text()
        return ImageList.from_mediawiki_content(mediawiki_content)

    def download_image(self, site: Site, image_name: str, i: int) -> None:
        logger.info(f"Download image ({i}): {image_name}")

        try:
            image = site.images[image_name]
            assert isinstance(image, Image)

            if not image.exists:
                logger.warning(f"Image does not exist on wiki: {image_name}")
                return

            self._output_dir.mkdir(parents=True, exist_ok=True)
            dest_path = self._output_dir / image_name

            if dest_path.is_file() and not self._yes:
                answer = input(f"Overwrite file '{str(dest_path)}' (Y/n/s): ")
                answer = answer.strip().lower()
                if answer == "s":
                    return
                elif answer != "y":
                    raise FileExistsError(f"Already exists file: '{str(dest_path)}'")

            with open(dest_path, "wb") as f:
                image.download(f)

            logger.info(f"Saved: {dest_path}")
        except BaseException as e:
            logger.error(f"Failed to download image '{image_name}': {e}")
            if not self._ignore_errors:
                raise

    def download_images(
        self,
        site: Site,
        image_names: Sequence[str],
    ) -> None:
        for i, name in enumerate(image_names, start=1):
            self.download_image(site, name, i)

    def run(self) -> None:
        if not self._image_page:
            raise ValueError("The 'image_page' argument is required")
        if not self._endpoint_path:
            raise ValueError("The 'endpoint_path' argument is required")

        image_list = self.read_image_list()

        if self._stdout:
            for name in image_list.images:
                print(name)
            return

        if not image_list.images:
            logger.warning("No images found in the image list")
            return

        logger.info(f"Found {len(image_list.images)} images to download")

        site = self.create_site()
        self.download_images(site, image_list.images)
