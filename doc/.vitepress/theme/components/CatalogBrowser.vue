<script setup>
import { ref, computed, onMounted } from 'vue'
import { useData, withBase } from 'vitepress'

const { lang: vpLang } = useData()

// VitePress reads lang like 'fr-FR', 'en-US', 'ar'. We only care about the
// first two chars for catalog field selection.
const SUPPORTED_LANGS = ['en', 'fr', 'es', 'pt', 'ar']

const initialLang = computed(() => {
  const raw = (vpLang.value || 'en').slice(0, 2).toLowerCase()
  return SUPPORTED_LANGS.includes(raw) ? raw : 'en'
})

const lang = ref(initialLang.value)
const data = ref(null)
const status = ref('loading') // 'loading' | 'ready' | 'error'
const errorMsg = ref('')
const openCats = ref(new Set())
const openSubs = ref(new Set())
const openDatasets = ref(new Set())
const search = ref('')

// EPSG:3857 world bbox used by the plugin's WMS preview.
const PREVIEW_BBOX =
  '-4554203.020722416,-4917533.4489256255,8081548.881484727,4906985.59447665'

// Pick the localized string from a multilingual field, or return the value as-is.
function tr(field, l = lang.value) {
  if (field == null) return ''
  if (typeof field === 'string' || typeof field === 'number') return String(field)
  if (typeof field === 'object') {
    return field[l] || field.en || field.fr || Object.values(field)[0] || ''
  }
  return ''
}

// Replace placeholders the plugin would normally resolve at provision time so
// public WMS layers can render in the preview. Layers that still contain
// unresolved placeholders (e.g. {country_alpha3}) are flagged unrenderable.
function resolveUrl(url) {
  if (!url) return ''
  return url.replace(/\{ECMWF_TOKEN\}/g, 'public')
}

function hasUnresolvedPlaceholder(url) {
  return /\{[a-zA-Z_]+\}/.test(url)
}

function buildWmsPreviewUrl(layer) {
  const base = resolveUrl(layer.wms_url || '')
  if (!base || hasUnresolvedPlaceholder(base)) return null
  const sep = base.includes('?') ? '&' : '?'
  const extra = layer.extra_params || {}
  const extraQs = Object.keys(extra)
    .filter((k) => extra[k] !== null && extra[k] !== undefined && extra[k] !== '')
    .map((k) => `${encodeURIComponent(k)}=${encodeURIComponent(extra[k])}`)
    .join('&')
  return (
    base +
    sep +
    'SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0' +
    '&LAYERS=' +
    encodeURIComponent(layer.layer_name || '') +
    '&CRS=EPSG:3857' +
    '&BBOX=' +
    PREVIEW_BBOX +
    '&WIDTH=320&HEIGHT=240' +
    '&FORMAT=image/png' +
    '&TRANSPARENT=true' +
    (extraQs ? '&' + extraQs : '')
  )
}

const stats = computed(() => {
  if (!data.value) return null
  let cats = 0,
    subs = 0,
    datasets = 0,
    layers = 0,
    byType = {}
  for (const c of data.value.categories || []) {
    cats++
    for (const sc of c.subcategories || []) {
      subs++
      for (const d of sc.datasets || []) {
        datasets++
        for (const l of d.layers || []) {
          layers++
          byType[l.type] = (byType[l.type] || 0) + 1
        }
      }
    }
  }
  return { cats, subs, datasets, layers, byType }
})

const filteredCategories = computed(() => {
  if (!data.value) return []
  const q = search.value.trim().toLowerCase()
  if (!q) return data.value.categories || []
  return (data.value.categories || [])
    .map((c) => {
      const subs = (c.subcategories || [])
        .map((sc) => {
          const ds = (sc.datasets || []).filter((d) => {
            const t = tr(d.title).toLowerCase()
            const ov = tr(d.metadata?.overview).toLowerCase()
            const src = String(d.metadata?.source || '').toLowerCase()
            const ln = (d.layers || []).some((l) =>
              String(l.layer_name || '').toLowerCase().includes(q),
            )
            return t.includes(q) || ov.includes(q) || src.includes(q) || ln
          })
          return { ...sc, datasets: ds }
        })
        .filter((sc) => sc.datasets.length > 0)
      return { ...c, subcategories: subs }
    })
    .filter((c) => c.subcategories.length > 0)
})

function catKey(ci) {
  return `c${ci}`
}
function subKey(ci, si) {
  return `c${ci}s${si}`
}
function dsKey(ci, si, di) {
  return `c${ci}s${si}d${di}`
}

function toggleCat(k) {
  openCats.value.has(k) ? openCats.value.delete(k) : openCats.value.add(k)
  openCats.value = new Set(openCats.value)
}
function toggleSub(k) {
  openSubs.value.has(k) ? openSubs.value.delete(k) : openSubs.value.add(k)
  openSubs.value = new Set(openSubs.value)
}
function toggleDs(k) {
  openDatasets.value.has(k)
    ? openDatasets.value.delete(k)
    : openDatasets.value.add(k)
  openDatasets.value = new Set(openDatasets.value)
}
function getLayerCountForCategory(category) {
  return (category.subcategories || []).reduce((total, subcategory) => {
    return total + (subcategory.datasets ? subcategory.datasets.length : 0)
  }, 0)
}

// Deterministic FNV-1a hash → stable badge color per distinct value.
function hashStr(s) {
  let h = 2166136261 >>> 0
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i)
    h = Math.imul(h, 16777619) >>> 0
  }
  return h
}

// Returns CSS custom properties for light and dark themes. Same hue both
// sides, swapped lightness so contrast stays readable.
function colorFor(value) {
  const v = String(value || '').trim() || '∅'
  const hue = hashStr(v) % 360
  return {
    '--cb-bg': `hsl(${hue} 75% 90%)`,
    '--cb-fg': `hsl(${hue} 55% 25%)`,
    '--cb-bg-dark': `hsl(${hue} 40% 22%)`,
    '--cb-fg-dark': `hsl(${hue} 80% 85%)`,
  }
}

function datasetTypes(ds) {
  const seen = new Set()
  const out = []
  for (const l of ds.layers || []) {
    if (l.type && !seen.has(l.type)) {
      seen.add(l.type)
      out.push(l.type)
    }
  }
  return out
}

function datasetSource(ds) {
  const raw = ds.metadata?.source
  if (raw == null || raw === '') return ''
  return typeof raw === 'object' ? tr(raw) : String(raw)
}
function expandAll() {
  if (!data.value) return
  const nc = new Set(),
    ns = new Set()
  ;(data.value.categories || []).forEach((c, ci) => {
    nc.add(catKey(ci))
    ;(c.subcategories || []).forEach((_, si) => ns.add(subKey(ci, si)))
  })
  openCats.value = nc
  openSubs.value = ns
}
function collapseAll() {
  openCats.value = new Set()
  openSubs.value = new Set()
  openDatasets.value = new Set()
}

onMounted(async () => {
  try {
    const url = withBase('/catalog.json')
    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    data.value = await res.json()
    status.value = 'ready'
    // Auto-open the first category on load so the user sees something.
    if (data.value.categories?.length) openCats.value.add(catKey(0))
  } catch (err) {
    status.value = 'error'
    errorMsg.value = err.message || String(err)
  }
})

const I18N = {
  en: {
    title: 'Embedded catalog browser',
    intro:
      'Browse the catalog shipped with the plugin. Expand a category to see its subcategories, then click a dataset to view its metadata and (for WMS layers) a preview.',
    search: 'Search by title, layer name, abstract, source…',
    lang: 'Catalog language',
    counters: ['categories', 'subcategories', 'datasets', 'layers'],
    loading: 'Loading catalog…',
    error: 'Failed to load catalog',
    expand: 'Expand all',
    collapse: 'Collapse all',
    version: 'Catalog version',
    type: 'Type',
    layerName: 'Layer name',
    wmsUrl: 'WMS URL',
    tileUrl: 'Tile URL',
    fileUrl: 'File URL',
    cogUrl: 'COG URL template',
    source: 'Source',
    function: 'Function',
    resolution: 'Resolution',
    coverage: 'Coverage',
    license: 'License',
    updateFreq: 'Update frequency',
    learnMore: 'Learn more',
    description: 'Description',
    preview: 'WMS preview',
    previewUnavailable:
      'Preview unavailable — the WMS URL contains unresolved placeholders (e.g. country code) or the remote server cannot be reached.',
    noPreviewType: 'No preview for this layer type.',
    publicFlag: 'Public',
    multiTemporal: 'Multi-temporal',
    initialVisible: 'Initially visible',
    autoUpdate: 'Auto-update interval (min)',
    nearRealtime: 'Near real-time',
    extraParams: 'Extra WMS params',
    popup: 'Enable popup',
    legendFromCapabilities: 'Load legend from WMS capabilities',
    noResults: 'No dataset matches your search.',
  },
  fr: {
    title: 'Explorer le catalogue embarqué',
    intro:
      'Parcourez le catalogue livré avec le plugin. Dépliez une catégorie pour voir ses sous-catégories, puis cliquez sur un dataset pour afficher ses métadonnées et (pour les couches WMS) une preview.',
    search: 'Rechercher par titre, nom de couche, résumé, source…',
    lang: 'Langue du catalogue',
    counters: ['catégories', 'sous-catégories', 'datasets', 'couches'],
    loading: 'Chargement du catalogue…',
    error: 'Échec du chargement du catalogue',
    expand: 'Tout déplier',
    collapse: 'Tout replier',
    version: 'Version du catalogue',
    type: 'Type',
    layerName: 'Nom de la couche',
    wmsUrl: 'URL WMS',
    tileUrl: 'URL des tuiles',
    fileUrl: 'URL du fichier',
    cogUrl: 'Gabarit URL COG',
    source: 'Source',
    function: 'Fonction',
    resolution: 'Résolution',
    coverage: 'Couverture',
    license: 'Licence',
    updateFreq: 'Fréquence de mise à jour',
    learnMore: 'En savoir plus',
    description: 'Description',
    preview: 'Aperçu WMS',
    previewUnavailable:
      'Aperçu indisponible — l\'URL WMS contient des placeholders non résolus (ex. code pays) ou le serveur distant n\'est pas joignable.',
    noPreviewType: 'Pas d\'aperçu pour ce type de couche.',
    publicFlag: 'Public',
    multiTemporal: 'Multi-temporel',
    initialVisible: 'Visible par défaut',
    autoUpdate: 'Intervalle d\'auto-update (min)',
    nearRealtime: 'Temps quasi-réel',
    extraParams: 'Paramètres WMS supplémentaires',
    popup: 'Popup activé',
    legendFromCapabilities: 'Légende issue des capabilities WMS',
    noResults: 'Aucun dataset ne correspond à votre recherche.',
  },
  es: {
    title: 'Explorar el catálogo incluido',
    intro:
      'Recorra el catálogo entregado con el plugin. Despliegue una categoría para ver sus subcategorías, después haga clic en un dataset para ver sus metadatos y (para las capas WMS) una vista previa.',
    search: 'Buscar por título, nombre de capa, abstract, fuente…',
    lang: 'Idioma del catálogo',
    counters: ['categorías', 'subcategorías', 'datasets', 'capas'],
    loading: 'Cargando el catálogo…',
    error: 'Error al cargar el catálogo',
    expand: 'Expandir todo',
    collapse: 'Colapsar todo',
    version: 'Versión del catálogo',
    type: 'Tipo',
    layerName: 'Nombre de la capa',
    wmsUrl: 'URL WMS',
    tileUrl: 'URL de teselas',
    fileUrl: 'URL del archivo',
    cogUrl: 'Plantilla URL COG',
    source: 'Fuente',
    function: 'Función',
    resolution: 'Resolución',
    coverage: 'Cobertura',
    license: 'Licencia',
    updateFreq: 'Frecuencia de actualización',
    learnMore: 'Más información',
    description: 'Descripción',
    preview: 'Vista previa WMS',
    previewUnavailable:
      'Vista previa no disponible — la URL WMS contiene marcadores sin resolver (p. ej. código de país) o no se puede contactar al servidor remoto.',
    noPreviewType: 'Sin vista previa para este tipo de capa.',
    publicFlag: 'Público',
    multiTemporal: 'Multi-temporal',
    initialVisible: 'Visible por defecto',
    autoUpdate: 'Intervalo de auto-actualización (min)',
    nearRealtime: 'Casi tiempo real',
    extraParams: 'Parámetros WMS adicionales',
    popup: 'Popup activado',
    legendFromCapabilities: 'Leyenda desde capabilities WMS',
    noResults: 'Ningún dataset coincide con su búsqueda.',
  },
  pt: {
    title: 'Explorar o catálogo embarcado',
    intro:
      'Percorra o catálogo entregue com o plugin. Expanda uma categoria para ver suas subcategorias, depois clique em um dataset para ver seus metadados e (para as camadas WMS) uma pré-visualização.',
    search: 'Buscar por título, nome da camada, abstract, fonte…',
    lang: 'Idioma do catálogo',
    counters: ['categorias', 'subcategorias', 'datasets', 'camadas'],
    loading: 'Carregando o catálogo…',
    error: 'Falha ao carregar o catálogo',
    expand: 'Expandir tudo',
    collapse: 'Recolher tudo',
    version: 'Versão do catálogo',
    type: 'Tipo',
    layerName: 'Nome da camada',
    wmsUrl: 'URL WMS',
    tileUrl: 'URL de tiles',
    fileUrl: 'URL do arquivo',
    cogUrl: 'Template URL COG',
    source: 'Fonte',
    function: 'Função',
    resolution: 'Resolução',
    coverage: 'Cobertura',
    license: 'Licença',
    updateFreq: 'Frequência de atualização',
    learnMore: 'Saiba mais',
    description: 'Descrição',
    preview: 'Pré-visualização WMS',
    previewUnavailable:
      'Pré-visualização indisponível — a URL WMS contém marcadores não resolvidos (ex.: código de país) ou o servidor remoto não está acessível.',
    noPreviewType: 'Sem pré-visualização para este tipo de camada.',
    publicFlag: 'Público',
    multiTemporal: 'Multi-temporal',
    initialVisible: 'Visível por padrão',
    autoUpdate: 'Intervalo de auto-update (min)',
    nearRealtime: 'Quase em tempo real',
    extraParams: 'Parâmetros WMS adicionais',
    popup: 'Popup ativado',
    legendFromCapabilities: 'Legenda a partir das capabilities WMS',
    noResults: 'Nenhum dataset corresponde à sua busca.',
  },
  ar: {
    title: 'استعراض الكتالوج المدمج',
    intro:
      'تصفّح الكتالوج المسلَّم مع المكوّن. وسّع فئة لرؤية فئاتها الفرعية، ثم انقر على مجموعة بيانات لعرض بياناتها الوصفية و(لطبقات WMS) معاينة.',
    search: 'ابحث بالعنوان أو اسم الطبقة أو الملخّص أو المصدر…',
    lang: 'لغة الكتالوج',
    counters: ['الفئات', 'الفئات الفرعية', 'مجموعات البيانات', 'الطبقات'],
    loading: 'جاري تحميل الكتالوج…',
    error: 'فشل تحميل الكتالوج',
    expand: 'توسيع الكل',
    collapse: 'طي الكل',
    version: 'إصدار الكتالوج',
    type: 'النوع',
    layerName: 'اسم الطبقة',
    wmsUrl: 'عنوان WMS',
    tileUrl: 'عنوان البلاط',
    fileUrl: 'عنوان الملف',
    cogUrl: 'قالب عنوان COG',
    source: 'المصدر',
    function: 'الوظيفة',
    resolution: 'الدقة',
    coverage: 'التغطية',
    license: 'الترخيص',
    updateFreq: 'تردد التحديث',
    learnMore: 'مزيد من المعلومات',
    description: 'الوصف',
    preview: 'معاينة WMS',
    previewUnavailable:
      'المعاينة غير متاحة — يحتوي عنوان WMS على عناصر نائبة لم تُحلّ (مثل رمز البلد) أو لا يمكن الوصول إلى الخادم البعيد.',
    noPreviewType: 'لا توجد معاينة لنوع الطبقة هذا.',
    publicFlag: 'عام',
    multiTemporal: 'متعدد الأزمنة',
    initialVisible: 'ظاهر افتراضيًا',
    autoUpdate: 'فاصل التحديث التلقائي (دقيقة)',
    nearRealtime: 'شبه فوري',
    extraParams: 'معلمات WMS إضافية',
    popup: 'تفعيل النافذة المنبثقة',
    legendFromCapabilities: 'تحميل وسيلة الإيضاح من قدرات WMS',
    noResults: 'لا توجد مجموعة بيانات تطابق بحثك.',
  },
}

const t = computed(() => I18N[lang.value] || I18N.en)
</script>

<template>
  <div class="cb">
    <div class="cb-header">
      <h2>{{ t.title }}</h2>
      <p class="cb-intro">{{ t.intro }}</p>
    </div>

    <div v-if="status === 'loading'" class="cb-state">{{ t.loading }}</div>
    <div v-else-if="status === 'error'" class="cb-state error">
      {{ t.error }}: {{ errorMsg }}
    </div>

    <template v-else>
      <div class="cb-toolbar">
        <input
          v-model="search"
          class="cb-input"
          type="search"
          :placeholder="t.search"
        />
        <label class="cb-langwrap">
          <span class="cb-langlabel">{{ t.lang }}</span>
          <select v-model="lang" class="cb-select">
            <option value="en">English</option>
            <option value="fr">Français</option>
            <option value="es">Español</option>
            <option value="pt">Português</option>
            <option value="ar">العربية</option>
          </select>
        </label>
        <div style="display: flex; gap: 0.5rem;">
          <button class="cb-btn" @click="expandAll">▼ {{ t.expand }}</button>
          <button class="cb-btn" @click="collapseAll">▶ {{ t.collapse }}</button>
        </div>
      </div>

      <div class="cb-stats" v-if="stats">
        <div><strong>{{ stats.cats }}</strong> {{ t.counters[0] }}</div>
        <div><strong>{{ stats.subs }}</strong> {{ t.counters[1] }}</div>
        <div><strong>{{ stats.datasets }}</strong> {{ t.counters[2] }}</div>
        <div><strong>{{ stats.layers }}</strong> {{ t.counters[3] }}</div>
        <div class="cb-version">
          {{ t.version }}: <code>{{ data.version }}</code>
        </div>
      </div>

      <div class="cb-tree" v-if="filteredCategories.length">
        <div
          v-for="(cat, ci) in filteredCategories"
          :key="catKey(ci)"
          class="cb-cat"
        >
          <button
            class="cb-cat-header"
            @click="toggleCat(catKey(ci))"
            :aria-expanded="openCats.has(catKey(ci))"
          >
            <span class="cb-arrow" :class="{ open: openCats.has(catKey(ci)) }">▶</span>
            <span class="cb-cat-title">{{ tr(cat.title) }}</span>
            <span class="cb-count">{{ getLayerCountForCategory(cat) }}</span>
          </button>
          <div v-if="openCats.has(catKey(ci))" class="cb-subs">
            <div
              v-for="(sub, si) in cat.subcategories"
              :key="subKey(ci, si)"
              class="cb-sub"
            >
              <button
                class="cb-sub-header"
                @click="toggleSub(subKey(ci, si))"
                :aria-expanded="openSubs.has(subKey(ci, si))"
              >
                <span
                  class="cb-arrow"
                  :class="{ open: openSubs.has(subKey(ci, si)) }"
                >▶</span>
                <span class="cb-sub-title">{{ tr(sub.title) }}</span>
                <span class="cb-count">{{ sub.datasets.length }}</span>
              </button>
              <div v-if="openSubs.has(subKey(ci, si))" class="cb-datasets">
                <div
                  v-for="(ds, di) in sub.datasets"
                  :key="dsKey(ci, si, di)"
                  class="cb-ds"
                >
                  <button
                    class="cb-ds-header"
                    @click="toggleDs(dsKey(ci, si, di))"
                    :aria-expanded="openDatasets.has(dsKey(ci, si, di))"
                  >
                    <span
                      class="cb-arrow"
                      :class="{ open: openDatasets.has(dsKey(ci, si, di)) }"
                    >▶</span>
                    <span class="cb-ds-title">{{ tr(ds.title) }}</span>
                    <span class="cb-ds-badges">
                      <span
                        v-for="ty in datasetTypes(ds)"
                        :key="'t-' + ty"
                        class="cb-badge cb-badge-tag"
                        :style="colorFor('type:' + ty)"
                        :title="t.type"
                      >{{ ty }}</span>
                      <span
                        v-if="datasetSource(ds)"
                        class="cb-badge cb-badge-tag"
                        :style="colorFor('src:' + datasetSource(ds))"
                        :title="t.source"
                      >{{ datasetSource(ds) }}</span>
                    </span>
                  </button>
                  <div
                    v-if="openDatasets.has(dsKey(ci, si, di))"
                    class="cb-detail"
                  >
                    <div class="cb-meta">
                      <div
                        v-if="tr(ds.metadata?.overview)"
                        class="cb-desc"
                      >
                        {{ tr(ds.metadata?.overview) }}
                      </div>
                      <table class="cb-table">
                        <tbody>
                          <tr v-if="ds.metadata?.source">
                            <td>{{ t.source }}</td>
                            <td>{{ tr(ds.metadata.source) }}</td>
                          </tr>
                          <tr v-if="tr(ds.metadata?.function)">
                            <td>{{ t.function }}</td>
                            <td>{{ tr(ds.metadata.function) }}</td>
                          </tr>
                          <tr v-if="tr(ds.metadata?.resolution)">
                            <td>{{ t.resolution }}</td>
                            <td>{{ tr(ds.metadata.resolution) }}</td>
                          </tr>
                          <tr v-if="tr(ds.metadata?.geographic_coverage)">
                            <td>{{ t.coverage }}</td>
                            <td>{{ tr(ds.metadata.geographic_coverage) }}</td>
                          </tr>
                          <tr v-if="tr(ds.metadata?.frequency_of_update)">
                            <td>{{ t.updateFreq }}</td>
                            <td>{{ tr(ds.metadata.frequency_of_update) }}</td>
                          </tr>
                          <tr v-if="ds.metadata?.license">
                            <td>{{ t.license }}</td>
                            <td>{{ tr(ds.metadata.license) }}</td>
                          </tr>
                          <tr>
                            <td>{{ t.publicFlag }}</td>
                            <td>{{ ds.public === false ? '—' : '✓' }}</td>
                          </tr>
                          <tr v-if="ds.multi_temporal">
                            <td>{{ t.multiTemporal }}</td>
                            <td>✓</td>
                          </tr>
                          <tr v-if="ds.initial_visible">
                            <td>{{ t.initialVisible }}</td>
                            <td>✓</td>
                          </tr>
                          <tr v-if="ds.auto_update_interval">
                            <td>{{ t.autoUpdate }}</td>
                            <td>{{ ds.auto_update_interval }}</td>
                          </tr>
                          <tr v-if="ds.near_realtime">
                            <td>{{ t.nearRealtime }}</td>
                            <td>✓</td>
                          </tr>
                          <tr v-if="ds.metadata?.learn_more">
                            <td>{{ t.learnMore }}</td>
                            <td>
                              <a
                                :href="resolveUrl(ds.metadata.learn_more)"
                                target="_blank"
                                rel="noopener"
                              >{{ ds.metadata.learn_more }}</a>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>

                    <div
                      v-for="(layer, li) in ds.layers"
                      :key="li"
                      class="cb-layer"
                    >
                      <div class="cb-layer-head">
                        <span class="cb-badge cb-badge-type">{{ layer.type }}</span>
                        <span class="cb-layer-name">{{
                          tr(layer.title) || layer.layer_name
                        }}</span>
                        <span v-if="layer.default" class="cb-badge cb-badge-default">default</span>
                      </div>
                      <table class="cb-table cb-layer-table">
                        <tbody>
                          <tr v-if="layer.layer_name">
                            <td>{{ t.layerName }}</td>
                            <td><code>{{ layer.layer_name }}</code></td>
                          </tr>
                          <tr v-if="layer.wms_url">
                            <td>{{ t.wmsUrl }}</td>
                            <td><code>{{ layer.wms_url }}</code></td>
                          </tr>
                          <tr v-if="layer.tile_url">
                            <td>{{ t.tileUrl }}</td>
                            <td><code>{{ layer.tile_url }}</code></td>
                          </tr>
                          <tr v-if="layer.file_url">
                            <td>{{ t.fileUrl }}</td>
                            <td><code>{{ layer.file_url }}</code></td>
                          </tr>
                          <tr v-if="layer.cog_url_template">
                            <td>{{ t.cogUrl }}</td>
                            <td><code>{{ layer.cog_url_template }}</code></td>
                          </tr>
                          <tr v-if="layer.extra_params && Object.keys(layer.extra_params).length">
                            <td>{{ t.extraParams }}</td>
                            <td>
                              <code>{{ JSON.stringify(layer.extra_params) }}</code>
                            </td>
                          </tr>
                          <tr v-if="layer.type === 'wms' && layer.popup">
                            <td>{{ t.popup }}</td>
                            <td>✓</td>
                          </tr>
                          <tr v-if="layer.type === 'wms' && layer.legend_from_capabilities">
                            <td>{{ t.legendFromCapabilities }}</td>
                            <td>✓</td>
                          </tr>
                        </tbody>
                      </table>

                      <div v-if="layer.type === 'wms'" class="cb-preview">
                        <div class="cb-preview-label">{{ t.preview }}</div>
                        <template v-if="buildWmsPreviewUrl(layer)">
                          <img
                            :src="buildWmsPreviewUrl(layer)"
                            :alt="layer.layer_name"
                            loading="lazy"
                            class="cb-preview-img"
                            @error="$event.target.classList.add('cb-img-failed')"
                          />
                          <div class="cb-img-fallback">{{ t.previewUnavailable }}</div>
                        </template>
                        <div v-else class="cb-preview-skip">
                          {{ t.previewUnavailable }}
                        </div>
                      </div>
                      <div v-else class="cb-preview-skip">
                        {{ t.noPreviewType }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="cb-state">{{ t.noResults }}</div>
    </template>
  </div>
</template>

<style scoped>
.cb {
  margin-top: 1rem;
}

.cb-header h2 {
  margin: 0 0 0.25rem;
}
.cb-intro {
  margin: 0 0 1rem;
  color: var(--vp-c-text-2);
  font-size: 0.95rem;
}

.cb-state {
  padding: 1rem;
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  color: var(--vp-c-text-2);
}
.cb-state.error {
  background: #fee2e2;
  color: #991b1b;
}

.cb-toolbar {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.cb-input {
  padding: 8px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 0.9rem;
}
.cb-langwrap {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.cb-langlabel {
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
}
.cb-select {
  padding: 6px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
}
.cb-btn {
  padding: 6px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  cursor: pointer;
  font-size: 0.85rem;
}
.cb-btn:hover {
  background: var(--vp-c-bg-soft);
}

.cb-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  padding: 0.6rem 1rem;
  margin-bottom: 0.75rem;
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  font-size: 0.9rem;
}
.cb-stats strong {
  color: var(--vp-c-brand-1);
  font-weight: 600;
}
.cb-version {
  margin-left: auto;
  color: var(--vp-c-text-2);
}

.cb-tree {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  overflow: hidden;
}
.cb-cat + .cb-cat,
.cb-sub + .cb-sub,
.cb-ds + .cb-ds {
  border-top: 1px solid var(--vp-c-divider);
}

button.cb-cat-header,
button.cb-sub-header,
button.cb-ds-header {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.9rem;
  background: transparent;
  border: 0;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.9rem;
  color: var(--vp-c-text-1);
  text-align: start;
}
button.cb-cat-header {
  background: var(--vp-c-bg-soft);
  font-weight: 600;
}
button.cb-sub-header {
  padding-inline-start: 2rem;
  font-weight: 500;
}
button.cb-ds-header {
  padding-inline-start: 3rem;
}
button.cb-cat-header:hover,
button.cb-sub-header:hover,
button.cb-ds-header:hover {
  background: var(--vp-c-bg-mute);
}

.cb-arrow {
  display: inline-block;
  font-size: 0.7rem;
  color: var(--vp-c-text-3);
  transition: transform 0.15s ease;
  width: 0.9rem;
}
.cb-arrow.open {
  transform: rotate(90deg);
}
[dir='rtl'] .cb-arrow {
  transform: rotate(180deg);
}
[dir='rtl'] .cb-arrow.open {
  transform: rotate(90deg);
}

.cb-count {
  margin-inline-start: auto;
  font-size: 0.75rem;
  font-weight: 400;
  color: var(--vp-c-text-3);
  background: var(--vp-c-bg-mute);
  padding: 1px 8px;
  border-radius: 999px;
}

.cb-badge {
  font-size: 0.7rem;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--vp-c-bg-mute);
  color: var(--vp-c-text-2);
  font-weight: 500;
  white-space: nowrap;
}
.cb-badge-type {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
}
.cb-badge-default {
  background: #fef3c7;
  color: #92400e;
}

/* Colored badges driven by inline CSS custom properties (computed via
   colorFor()). Dark theme swaps the bg/fg pair so contrast holds. */
.cb-badge-tag {
  background: var(--cb-bg);
  color: var(--cb-fg);
  font-weight: 600;
  letter-spacing: 0.01em;
}
.dark .cb-badge-tag {
  background: var(--cb-bg-dark);
  color: var(--cb-fg-dark);
}

.cb-ds-badges {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin-inline-start: auto;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.cb-detail {
  padding: 0.75rem 1rem 1rem 3.5rem;
  background: var(--vp-c-bg);
  border-top: 1px solid var(--vp-c-divider);
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 1rem;
}

.cb-desc {
  font-size: 0.9rem;
  color: var(--vp-c-text-1);
  margin-bottom: 0.5rem;
}

.cb-table {
  width: 100%;
  font-size: 0.85rem;
  border-collapse: collapse;
}
.cb-table td {
  padding: 4px 8px;
  vertical-align: top;
  border-bottom: 1px solid var(--vp-c-divider);
}
.cb-table td:first-child {
  width: 9rem;
  color: var(--vp-c-text-2);
  font-weight: 500;
}
.cb-table td code {
  font-size: 0.78rem;
  word-break: break-all;
}

.cb-layer {
  padding: 0.75rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg-soft);
}

.cb-layer-head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.cb-layer-name {
  font-weight: 600;
  font-size: 0.9rem;
}

.cb-layer-table {
  margin-bottom: 0.5rem;
}

.cb-preview {
  margin-top: 0.5rem;
}
.cb-preview-label {
  font-size: 0.75rem;
  color: var(--vp-c-text-3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}
.cb-preview-img {
  width: 320px;
  height: 240px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background:
    repeating-conic-gradient(var(--vp-c-bg-mute) 0% 25%, transparent 25% 50%) 50% / 16px 16px;
  display: block;
}
.cb-preview-img.cb-img-failed {
  display: none;
}
.cb-preview-img.cb-img-failed + .cb-img-fallback {
  display: block;
}
.cb-img-fallback,
.cb-preview-skip {
  display: none;
  font-size: 0.8rem;
  color: var(--vp-c-text-3);
  font-style: italic;
}
.cb-preview-img.cb-img-failed ~ .cb-img-fallback,
.cb-preview > .cb-preview-skip,
.cb-layer > .cb-preview-skip {
  display: block;
}
</style>
