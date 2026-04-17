import hashlib
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class PluginSettings(models.Model):
    """
    Singleton settings for the Dataset Helper plugin.
    Stores per-Climweb configuration: language, ECMWF token, eStation URL.
    """

    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('fr', 'Français'),
        ('es', 'Español'),
        ('pt', 'Português'),
        ('ar', 'العربية'),
    )

    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='en',
        verbose_name=_("Language"),
        help_text=_("Language for imported catalog labels"),
    )
    ecmwf_token = models.CharField(
        max_length=255,
        default='public',
        verbose_name=_("ECMWF API Token"),
        help_text=_("Token for ECMWF eccharts WMS service"),
    )
    estation_url = models.URLField(
        max_length=500,
        blank=True,
        default='',
        verbose_name=_("Local eStation URL"),
        help_text=_("If set, only eStation products available on this local instance will be imported"),
    )
    country_alpha3 = models.CharField(
        max_length=3,
        blank=True,
        default='',
        verbose_name=_("Country code (alpha-3)"),
        help_text=_("ISO 3166-1 alpha-3 country code used for URL placeholder substitution (e.g. bfa)"),
    )

    class Meta:
        verbose_name = _("Plugin Settings")
        verbose_name_plural = _("Plugin Settings")

    def __str__(self):
        return f"Plugin Settings (lang={self.language})"

    def save(self, *args, **kwargs):
        # Enforce singleton: always use pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class CatalogEntry(models.Model):
    """
    A layer in the plugin's catalog. Tracks what layers are available,
    whether the admin wants them, and whether they've been provisioned
    into Climweb's geomanager DB.
    """

    LAYER_TYPE_WMS = 'wms'
    LAYER_TYPE_RASTER_TILE = 'raster_tile'
    LAYER_TYPE_VECTOR_TILE = 'vector_tile'
    LAYER_TYPE_RASTER_FILE = 'raster_file'
    LAYER_TYPE_VECTOR_FILE = 'vector_file'
    LAYER_TYPE_CHOICES = (
        (LAYER_TYPE_WMS, _('WMS')),
        (LAYER_TYPE_RASTER_TILE, _('Raster Tile')),
        (LAYER_TYPE_VECTOR_TILE, _('Vector Tile')),
        (LAYER_TYPE_RASTER_FILE, _('Raster File')),
        (LAYER_TYPE_VECTOR_FILE, _('Vector File')),
    )

    ORIGIN_CONFIG = 'config'
    ORIGIN_MANUAL = 'manual'
    ORIGIN_WMS_IMPORT = 'wms_import'
    ORIGIN_CHOICES = (
        (ORIGIN_CONFIG, _('From configuration')),
        (ORIGIN_MANUAL, _('Manually added')),
        (ORIGIN_WMS_IMPORT, _('WMS import')),
    )

    STATUS_SYNCED = 'synced'
    STATUS_PENDING_ADD = 'pending_add'
    STATUS_PENDING_REMOVE = 'pending_remove'
    STATUS_DISABLED = 'disabled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # --- Identity ---
    product_code = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Product code"),
        help_text=_("Unique identifier. For config entries this comes from the CSV/JSON. "
                     "For manual/WMS entries it is auto-generated."),
    )
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    summary = models.TextField(blank=True, default='')

    # --- Layer type ---
    layer_type = models.CharField(
        max_length=20,
        choices=LAYER_TYPE_CHOICES,
        default=LAYER_TYPE_WMS,
        verbose_name=_("Layer type"),
    )

    # --- Hierarchy (resolved to Climweb objects at provision time) ---
    category_title = models.CharField(max_length=255, verbose_name=_("Category"))
    category_icon = models.CharField(max_length=50, default='map')
    subcategory_title = models.CharField(max_length=255, verbose_name=_("Subcategory"))

    # --- WMS configuration ---
    layer_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name=_("WMS layer name"),
        help_text=_("Layer identifier as returned by WMS GetCapabilities"),
    )
    wms_url = models.CharField(max_length=500, blank=True, default='', verbose_name=_("WMS base URL"))
    layer_title = models.CharField(max_length=255, blank=True, default='')
    extra_params_json = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Extra WMS params"),
        help_text=_("Additional query parameters for WMS requests (JSON object)"),
    )

    # --- Tile configuration (raster_tile, vector_tile) ---
    tile_url = models.CharField(
        max_length=500, blank=True, default='',
        verbose_name=_("Tile URL"),
        help_text=_("URL template with {z}/{x}/{y} placeholders, or a .pmtiles file URL when is_pmtiles is set"),
    )
    is_pmtiles = models.BooleanField(
        default=False,
        verbose_name=_("PMTiles format"),
        help_text=_("For vector_tile layers: treat tile_url as a PMTiles archive URL instead of an XYZ template"),
    )

    # --- File configuration (raster_file, vector_file) ---
    file_url = models.CharField(
        max_length=500, blank=True, default='',
        verbose_name=_("File URL"),
        help_text=_("URL to a remote file. May contain {country_alpha3} placeholder."),
    )

    # --- Render layers (vector_tile, vector_file) ---
    render_layers_json = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Render layers"),
        help_text=_("MapLibre GL style layer definitions (JSON array)"),
    )

    # --- Legend configuration ---
    legend_json = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Legend"),
        help_text=_("Custom legend definition: {type, items: [{name, color}]}"),
    )

    # --- Metadata (denormalized from config) ---
    meta_source = models.CharField(max_length=255, blank=True, default='')
    meta_resolution = models.CharField(max_length=255, blank=True, default='')
    meta_geographic_coverage = models.CharField(max_length=255, blank=True, default='')
    meta_license = models.CharField(max_length=255, blank=True, default='')
    meta_frequency_of_update = models.CharField(max_length=255, blank=True, default='')
    meta_function = models.TextField(blank=True, default='')
    meta_overview = models.TextField(blank=True, default='')
    meta_learn_more = models.URLField(max_length=500, blank=True, default='')

    # --- Dataset properties ---
    multi_temporal = models.BooleanField(default=True)

    # --- State ---
    origin = models.CharField(
        max_length=20,
        choices=ORIGIN_CHOICES,
        default=ORIGIN_CONFIG,
    )
    enabled = models.BooleanField(
        default=True,
        verbose_name=_("Enabled"),
        help_text=_("Whether this entry should be provisioned in Climweb"),
    )
    dataset_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name=_("Climweb Dataset ID"),
        help_text=_("UUID of the corresponding Dataset in geomanager, if provisioned"),
    )

    # --- Ordering ---
    category_order = models.IntegerField(default=0, verbose_name=_("Category sort order"))
    subcategory_order = models.IntegerField(default=0, verbose_name=_("Subcategory sort order"))
    entry_order = models.IntegerField(default=0, verbose_name=_("Entry sort order"))

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Catalog Entry")
        verbose_name_plural = _("Catalog Entries")
        ordering = ['category_order', 'subcategory_order', 'entry_order', 'title']

    def __str__(self):
        return f"{self.category_title} > {self.subcategory_title} > {self.title}"

    @property
    def is_provisioned(self):
        return self.dataset_id is not None

    @property
    def status(self):
        if self.enabled and self.is_provisioned:
            return self.STATUS_SYNCED
        elif self.enabled and not self.is_provisioned:
            return self.STATUS_PENDING_ADD
        elif not self.enabled and self.is_provisioned:
            return self.STATUS_PENDING_REMOVE
        return self.STATUS_DISABLED

    @staticmethod
    def generate_product_code(identifier, url, origin='manual', layer_type='wms'):
        key = f"{layer_type}:{identifier}:{url}"
        digest = hashlib.md5(key.encode()).hexdigest()[:12]
        return f"{origin}_{digest}"
