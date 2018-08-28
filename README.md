Name
----
gpo-zugaina-dl - Download overlay, category or package ebuilds from gpo.zugaina.org

Synopsis
--------
Usage: gpo-zugaina-dl [options]

Options:
  -h, --help            show this help message and exit
  -s TEXT|CATEGORY/PACKAGE, --search=TEXT|CATEGORY/PACKAGE
                        search a package
  -l LIMIT, --limit=LIMIT
                        set max limit matches to display (only available with -s option)
  -d PREFIX OVERLAY CATEGORY/PACKAGE, --download=PREFIX OVERLAY CATEGORY/PACKAGE
                        download package from overlay
  -p, --pretend         display what will downloaded (only available with -d option)
  -v, --verbose         run in verbose mode (only available with -d option)


Parameters
----------
    TEXT                 a text search
    LIMIT                number of matches to display
    PREFIX               destination of downloaded files
    OVERLAY              name of overlay
    CATEGORY/PACKAGE     category/package that you want download

Options
-------
    -v, --verbose   tree print of downloaded files
    -p, --pretend   display what will downloaded
    -h, --help      display this help and exit

Examples
--------
    gpo-zugaina-dl -s fire                                      ->  search package that match "fire"
    gpo-zugaina-dl -s www-client/firefox                        ->  view all overlay where "www-client/firefox" is present
    gpo-zugaina-dl -d my_prefix_dir mozilla www-client/firefox  ->  download in "my_prefix_dir" "mozilla www-client/firefox" from "mozilla" overlay
