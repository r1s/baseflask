# -*- coding: utf-8 -*-
import inspect
import os
import pkgutil
from itertools import chain
from flask import Flask, Blueprint
import imp
from sqlalchemy.ext.declarative import DeclarativeMeta
from werkzeug.utils import import_string
from ext import Base

MODULE_EXTENSIONS = tuple([suff[0] for suff in imp.get_suffixes()])


class NoContextProcessorException(Exception):
    pass


class NoBlueprintException(Exception):
    pass


class NoExtensionException(Exception):
    pass


class AppFactory(object):

    def __init__(self, config, envvar='PROJECT_SETTINGS', bind_db_object=True):
        self.app_config = config
        self.app_envvar = os.environ.get(envvar, False)
        self.bind_db_object = bind_db_object

    def get_app(self, app_module_name, **kwargs):
        self.app = Flask(app_module_name, **kwargs)
        self.app.debug_log_format = self.app_config.DEBUG_LOG_FORMAT
        self.app.config.from_object(self.app_config)
        self.app.config.from_envvar(self.app_envvar, silent=True)

        self._bind_extensions()
        self._register_blueprints()
        self._register_context_processors()

        return self.app

    def _get_imported_stuff_by_path(self, module_name):
        module = import_string(module_name)
        return module

    def _bind_extensions(self):
        for ext_definition in self.app.config.get('EXTENSIONS', []):
            module_name, e_name = ext_definition.rsplit('.', 1)
            module = self._get_imported_stuff_by_path(module_name)
            if not hasattr(module, e_name):
                raise NoExtensionException('No {e_name} extension found'.format(e_name=e_name))
            ext = getattr(module, e_name)
            if getattr(ext, 'init_app', False):
                ext.init_app(self.app)
            else:
                ext(self.app)

    def _register_context_processors(self):
        for processor_definition in self.app.config.get('CONTEXT_PROCESSORS', []):
            module_name, p_name = processor_definition.rsplit('.', 1)
            module = self._get_imported_stuff_by_path(module_name)
            if hasattr(module, p_name):
                self.app.context_processor(getattr(module, p_name))
            else:
                raise NoContextProcessorException('No {cp_name} context processor found'.format(cp_name=p_name))

    def _register_blueprints(self):
        for blueprint_definition in self.app.config.get('BLUEPRINTS', []):
            module_name, blueprint_name = blueprint_definition.rsplit('.', 1)
            module = self._get_imported_stuff_by_path(module_name)

            blueprint_object = getattr(module, blueprint_name, None)
            if blueprint_object and isinstance(blueprint_object, Blueprint):
                # register routes
                self._register_routes(module, blueprint_object)
                # take and register models
                list(self._get_models(module.__name__))
                # register blueprint
                self.app.register_blueprint(blueprint_object)
            else:
                raise NoBlueprintException('No {bp_name} blueprint found'.format(bp_name=blueprint_name))

    def _get_submodules(self, module):
        for importer, module_name, is_pkg in pkgutil.iter_modules([os.path.dirname(module.__file__)]):
            sub_module = importer.find_module(module_name).load_module(module_name)
            if is_pkg:
                for module in self._get_submodules(sub_module):
                    yield module
            else:
                yield sub_module

    def _get_classes(self, module, with_submodules=True):
        module_classes = (view_class for view_name, view_class in inspect.getmembers(module)
                          if inspect.isclass(view_class))
        submodules_classes = ()

        if with_submodules and module.__file__[:module.__file__.rindex('.')].endswith('__init__'):
            submodules_classes = chain((module_class for module_class in inspect.getmembers(sub_module))
                                       for sub_module in self._get_submodules(module))
        return module_classes, submodules_classes

    def _get_route_views_from_module(self, blueprint_name, module_name):
        views_name = 'views'
        module_views_name = '{0}.{1}'.format(module_name, views_name)

        try:
            module_views = import_string(module_views_name)
        except (ImportError, ) as e:
            raise StopIteration()

        route_attr = 'route'
        route_blueprint_attr = 'blueprint'

        for view_class in chain(*self._get_classes(module_views)):
            if not hasattr(view_class, route_attr):
                continue

            route_blueprint = getattr(view_class, route_attr).get(route_blueprint_attr)
            if route_blueprint == blueprint_name:
                yield view_class
            else:
                self.app.logger.error('Blueprint name: {bp_name} is not {route_bp_name} in view: {view}'.
                                      format(bp_name=blueprint_name, route_bp_name=route_blueprint, view=view_class))

    def _get_models(self, module_name):
        models_name = 'models'
        module_models_name = '{0}.{1}'.format(module_name, models_name)

        try:
            module_models = import_string(module_models_name)
        except (ImportError, ) as e:
            raise StopIteration()

        for model_class in chain(*self._get_classes(module_models)):
            if isinstance(model_class, DeclarativeMeta) and model_class != Base:
                yield model_class

    def _register_route(self, blueprint, view):
        blueprint.add_url_rule(view.route.get('rule'), view_func=view.as_view(view.route.get('name')))

    def _register_routes(self, module, blueprint_object):
        for route_view in self._get_route_views_from_module(blueprint_object.name, module.__name__):
            self._register_route(blueprint_object, route_view)
