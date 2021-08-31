from collections import defaultdict

from django.db import models
from django.contrib.contenttypes.models import ContentType


class ContentTypeManager(models.Manager):
    def get_by_natural_key(self, app_label, model):

        return self.get(app_label=app_label, model=model)

    def _get_opts(self, model, for_concrete_model):
        if for_concrete_model:
            model = model._meta.concrete_model
        return model._meta

    def get_for_model(self, model, for_concrete_model=True):
        opts = self._get_opts(model, for_concrete_model)
        try:
            ct = self.get(app_label=opts.app_label, model=opts.model_name)
        except self.model.DoesNotExist:
            ct, created = self.get_or_create(
                app_label=opts.app_label,
                model=opts.model_name,
            )
        return ct

    def get_for_models(self, *models, for_concrete_models=True):
        """
        Given *models, return a dictionary mapping {model: content_type}.
        """
        results = {}
        # Models that aren't already in the cache.
        needed_app_labels = set()
        needed_models = set()
        # Mapping of opts to the list of models requiring it.
        needed_opts = defaultdict(list)
        for model in models:
            opts = self._get_opts(model, for_concrete_models)
            needed_app_labels.add(opts.app_label)
            needed_models.add(opts.model_name)
            needed_opts[opts].append(model)
        if needed_opts:
            # Lookup required content types from the DB.
            cts = self.filter(
                app_label__in=needed_app_labels,
                model__in=needed_models
            )
            for ct in cts:
                opts_models = needed_opts.pop(ct.model_class()._meta, [])
                for model in opts_models:
                    results[model] = ct
        # Create content types that weren't in the cache or DB.
        for opts, opts_models in needed_opts.items():
            ct = self.create(
                app_label=opts.app_label,
                model=opts.model_name,
            )
            for model in opts_models:
                results[model] = ct
        return results

    def get_for_id(self, id):
        """
        Lookup a ContentType by ID. Use the same shared cache as get_for_model
        (though ContentTypes are not created on-the-fly by get_by_id).
        """
        ct = self.get(pk=id)
        return ct


class ProxyContentType(ContentType):
    objects = ContentTypeManager()

    class Meta:
        managed = False
        proxy = True