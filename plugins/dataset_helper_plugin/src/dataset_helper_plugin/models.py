import hashlib
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class CatalogEntry(models.Model):
    """
    A layer in the plugin's catalog. Tracks what layers are available,
    whether the admin wants them, and whether they've been provisioned
    into Climweb's geomanager DB.
    """

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
    description = models.TextField(blank=True, default='')

    # --- Hierarchy (resolved to Climweb objects at provision time) ---
    category_title = models.CharField(max_length=255, verbose_name=_("Category"))
    category_icon = models.CharField(max_length=50, default='map')
    subcategory_title = models.CharField(max_length=255, verbose_name=_("Subcategory"))

    # --- WMS configuration ---
    layer_name = models.CharField(
        max_length=255,
        verbose_name=_("WMS layer name"),
        help_text=_("Layer identifier as returned by WMS GetCapabilities"),
    )
    wms_url = models.URLField(max_length=500, verbose_name=_("WMS base URL"))
    layer_title = models.CharField(max_length=255, blank=True, default='')

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

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Catalog Entry")
        verbose_name_plural = _("Catalog Entries")
        ordering = ['category_title', 'subcategory_title', 'title']

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
    def generate_product_code(layer_name, wms_url, origin='manual'):
        key = f"{layer_name}:{wms_url}"
        digest = hashlib.md5(key.encode()).hexdigest()[:12]
        return f"{origin}_{digest}"
