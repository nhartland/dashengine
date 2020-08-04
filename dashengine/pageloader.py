""" Pageloader Module
    Provides functionality for loading all the pages implemented in the project.
"""
# System
import pkgutil
import importlib


def page_loader(roots: list) -> dict:
    """ Reads page modules from subdirectories specified in the `roots` list,
    and returns them in a dictionary keyed by module.ROUTE. """
    import logging

    page_dict = {}
    for root in roots:
        for importer, package_name, _ in pkgutil.iter_modules([root]):
            full_package_name = "%s.%s" % (root, package_name)
            module = importlib.import_module(full_package_name)
            route = module.ROUTE
            logging.info(f'Page module "{package_name}" loaded at route "{route}"')
            if route in page_dict:
                raise RuntimeError(
                    f'Page module "{package_name}" tried to load at already existing route "{route}"'
                )
            page_dict[route] = module
    return page_dict
