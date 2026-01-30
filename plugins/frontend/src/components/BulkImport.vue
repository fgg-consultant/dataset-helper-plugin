<script setup lang="ts">
import { ref, computed } from 'vue'
import IconLoader2 from '@/__icons/IconLoader2.vue'
import IconCheck from '@/__icons/IconCheck.vue'
import IconAlertTriangle from '@/__icons/IconAlertTriangle.vue'

interface BulkConfig {
  categories: CategoryConfig[]
}

interface CategoryConfig {
  title: string
  icon?: string
  subcategories: SubcategoryConfig[]
}

interface SubcategoryConfig {
  title: string
  datasets: DatasetConfig[]
}

interface MetadataConfig {
  title?: string
  subtitle?: string
  function?: string
  resolution?: string
  geographic_coverage?: string
  source?: string
  license?: string
  frequency_of_update?: string
  overview?: string
  cautions?: string
  citation?: string
  download_data?: string
  learn_more?: string
}

interface DatasetConfig {
  title: string
  description?: string
  multi_temporal?: boolean
  metadata?: MetadataConfig
  layers: LayerConfig[]
}

interface LayerConfig {
  type?: 'wms' | 'raster_file' | 'vector_file' | 'raster_tile' | 'vector_tile'
  title?: string
  layer_name: string
  wms_url: string
  default?: boolean
  wms_version?: string
  wms_format?: string
  wms_srs?: string
}

interface ImportResults {
  status: string
  message: string
  categories_created: number
  categories_existing: number
  subcategories_created: number
  subcategories_existing: number
  datasets_created: number
  datasets_skipped: number
  layers_created: number
  metadata_created: number
  errors: string[]
}

const jsonInput = ref('')
const loading = ref(false)
const validationMessage = ref('')
const validationStatus = ref<'none' | 'valid' | 'invalid'>('none')
const results = ref<ImportResults | null>(null)
const copyButtonText = ref('Copy')

const sampleConfig: BulkConfig = {
  categories: [
    {
      title: 'Vegetation',
      icon: 'leaf',
      subcategories: [
        {
          title: 'NDVI Products',
          datasets: [
            {
              title: 'NDVI from CGLS (1km)',
              description: 'Normalized Difference Vegetation Index',
              multi_temporal: true,
              metadata: {
                title: 'NDVI from CGLS',
                function: 'Vegetation greenness indicator',
                resolution: '1km',
                geographic_coverage: 'Africa',
                source: 'Copernicus Global Land Service',
                frequency_of_update: 'Dekadal',
              },
              layers: [
                {
                  type: 'wms',
                  title: 'NDVI Default',
                  layer_name: 'vgt-ndvi_vgt-pv-olci_ndvi',
                  wms_url: 'https://estation.jrc.ec.europa.eu/geoserver/wms',
                  default: true,
                },
              ],
            },
          ],
        },
      ],
    },
  ],
}

const parsedConfig = computed(() => {
  if (!jsonInput.value.trim()) return null
  try {
    return JSON.parse(jsonInput.value) as BulkConfig
  } catch {
    return null
  }
})

const configStats = computed(() => {
  const config = parsedConfig.value
  if (!config) return null

  let categories = 0
  let subcategories = 0
  let datasets = 0
  let layers = 0

  if (config.categories) {
    categories = config.categories.length
    config.categories.forEach((cat) => {
      if (cat.subcategories) {
        subcategories += cat.subcategories.length
        cat.subcategories.forEach((sub) => {
          if (sub.datasets) {
            datasets += sub.datasets.length
            sub.datasets.forEach((ds) => {
              if (ds.layers) {
                layers += ds.layers.length
              }
            })
          }
        })
      }
    })
  }

  return { categories, subcategories, datasets, layers }
})

function validateJson() {
  if (!jsonInput.value.trim()) {
    validationStatus.value = 'invalid'
    validationMessage.value = 'Please enter a JSON configuration'
    return false
  }

  try {
    const config = JSON.parse(jsonInput.value) as BulkConfig

    if (!config.categories || !Array.isArray(config.categories) || config.categories.length === 0) {
      validationStatus.value = 'invalid'
      validationMessage.value = 'Missing or empty categories array'
      return false
    }

    // Validate structure
    for (const cat of config.categories) {
      if (!cat.title) {
        validationStatus.value = 'invalid'
        validationMessage.value = 'Category missing title field'
        return false
      }
      for (const sub of cat.subcategories || []) {
        if (!sub.title) {
          validationStatus.value = 'invalid'
          validationMessage.value = `Subcategory missing title in category "${cat.title}"`
          return false
        }
        for (const ds of sub.datasets || []) {
          if (!ds.title) {
            validationStatus.value = 'invalid'
            validationMessage.value = `Dataset missing title in "${cat.title}/${sub.title}"`
            return false
          }
          for (const layer of ds.layers || []) {
            if (!layer.layer_name || !layer.wms_url) {
              validationStatus.value = 'invalid'
              validationMessage.value = `Layer missing layer_name or wms_url in dataset "${ds.title}"`
              return false
            }
          }
        }
      }
    }

    validationStatus.value = 'valid'
    validationMessage.value = `Valid: ${configStats.value?.categories} categories, ${configStats.value?.subcategories} subcategories, ${configStats.value?.datasets} datasets, ${configStats.value?.layers} layers`
    return true
  } catch (e) {
    validationStatus.value = 'invalid'
    validationMessage.value = `Invalid JSON: ${(e as Error).message}`
    return false
  }
}

function loadSample() {
  jsonInput.value = JSON.stringify(sampleConfig, null, 2)
  validateJson()
}

async function copySample() {
  try {
    await navigator.clipboard.writeText(JSON.stringify(sampleConfig, null, 2))
    copyButtonText.value = 'Copied!'
    setTimeout(() => {
      copyButtonText.value = 'Copy'
    }, 2000)
  } catch {
    copyButtonText.value = 'Failed'
    setTimeout(() => {
      copyButtonText.value = 'Copy'
    }, 2000)
  }
}

async function runImport() {
  if (!validateJson()) return

  loading.value = true
  results.value = null

  try {
    const config = JSON.parse(jsonInput.value)

    // Send to parent window (Django template) via postMessage
    window.postMessage(
      {
        type: 'vue-bulk-import',
        config,
      },
      '*',
    )
  } catch (error) {
    results.value = {
      status: 'error',
      message: `Import failed: ${(error as Error).message}`,
      categories_created: 0,
      categories_existing: 0,
      subcategories_created: 0,
      subcategories_existing: 0,
      datasets_created: 0,
      datasets_skipped: 0,
      layers_created: 0,
      metadata_created: 0,
      errors: [],
    }
  }

  loading.value = false
}

// Listen for import results from parent
window.addEventListener('message', (event) => {
  if (event.data.type === 'bulk-import-result') {
    results.value = event.data.results
    loading.value = false
  }
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <div>
      <h2 class="text-2xl font-bold mb-2">Bulk Import</h2>
      <p class="text-gray-600">
        Import categories, subcategories, datasets and layers from a JSON configuration.
      </p>
    </div>

    <!-- Sample config toggle -->
    <details class="bg-gray-100 rounded-lg p-4">
      <summary class="cursor-pointer font-medium text-gray-700">View sample JSON format</summary>
      <div class="mt-4">
        <pre
          class="bg-gray-800 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm"
        >{{ JSON.stringify(sampleConfig, null, 2) }}</pre>
        <div class="mt-3 flex gap-3">
          <button
            @click="copySample"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
            {{ copyButtonText }}
          </button>
          <button
            @click="loadSample"
            class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
          >
            Load in Editor
          </button>
        </div>
      </div>
    </details>

    <!-- JSON Input -->
    <div>
      <label class="block mb-2 font-medium text-gray-700">JSON Configuration</label>
      <textarea
        v-model="jsonInput"
        class="w-full h-96 font-mono text-sm p-4 border border-gray-300 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20"
        placeholder="Paste your JSON configuration here..."
        @input="validationStatus = 'none'"
      ></textarea>
    </div>

    <!-- Config stats preview -->
    <div
      v-if="configStats && validationStatus === 'valid'"
      class="flex gap-4 text-sm text-gray-600 flex-wrap"
    >
      <span class="px-3 py-1 bg-emerald-100 text-emerald-700 rounded"
        >{{ configStats.categories }} categories</span
      >
      <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded"
        >{{ configStats.subcategories }} subcategories</span
      >
      <span class="px-3 py-1 bg-purple-100 text-purple-700 rounded"
        >{{ configStats.datasets }} datasets</span
      >
      <span class="px-3 py-1 bg-orange-100 text-orange-700 rounded"
        >{{ configStats.layers }} layers</span
      >
    </div>

    <!-- Actions -->
    <div class="flex gap-4 items-center flex-wrap">
      <button
        @click="validateJson"
        class="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
      >
        Validate
      </button>
      <button
        @click="runImport"
        :disabled="loading || validationStatus !== 'valid'"
        class="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
      >
        <IconLoader2 v-if="loading" class="h-5 w-5 animate-spin" />
        <span>{{ loading ? 'Importing...' : 'Import' }}</span>
      </button>

      <!-- Validation message -->
      <div v-if="validationStatus !== 'none'" class="flex items-center gap-2">
        <IconCheck v-if="validationStatus === 'valid'" class="h-5 w-5 text-emerald-600" />
        <IconAlertTriangle v-else class="h-5 w-5 text-red-500" />
        <span
          :class="validationStatus === 'valid' ? 'text-emerald-600' : 'text-red-500'"
          class="text-sm"
        >
          {{ validationMessage }}
        </span>
      </div>
    </div>

    <!-- Results -->
    <div
      v-if="results"
      class="p-6 rounded-lg"
      :class="results.status === 'success' ? 'bg-emerald-50 border border-emerald-200' : 'bg-red-50 border border-red-200'"
    >
      <h3 class="text-lg font-bold mb-4" :class="results.status === 'success' ? 'text-emerald-800' : 'text-red-800'">
        {{ results.message }}
      </h3>

      <div v-if="results.status === 'success'" class="grid grid-cols-2 md:grid-cols-6 gap-4">
        <div class="bg-white p-4 rounded-lg text-center">
          <div class="text-3xl font-bold text-emerald-600">{{ results.categories_created }}</div>
          <div class="text-sm text-gray-600">Categories</div>
        </div>
        <div class="bg-white p-4 rounded-lg text-center">
          <div class="text-3xl font-bold text-emerald-600">{{ results.subcategories_created }}</div>
          <div class="text-sm text-gray-600">Subcategories</div>
        </div>
        <div class="bg-white p-4 rounded-lg text-center">
          <div class="text-3xl font-bold text-emerald-600">{{ results.datasets_created }}</div>
          <div class="text-sm text-gray-600">Datasets</div>
        </div>
        <div class="bg-white p-4 rounded-lg text-center">
          <div class="text-3xl font-bold text-emerald-600">{{ results.layers_created }}</div>
          <div class="text-sm text-gray-600">Layers</div>
        </div>
        <div class="bg-white p-4 rounded-lg text-center">
          <div class="text-3xl font-bold text-blue-600">{{ results.metadata_created }}</div>
          <div class="text-sm text-gray-600">Metadata</div>
        </div>
        <div class="bg-white p-4 rounded-lg text-center">
          <div class="text-3xl font-bold text-amber-600">{{ results.datasets_skipped }}</div>
          <div class="text-sm text-gray-600">Skipped</div>
        </div>
      </div>

      <div v-if="results.errors && results.errors.length > 0" class="mt-4">
        <h4 class="font-medium text-gray-700 mb-2">Warnings / Skipped Items:</h4>
        <ul class="bg-white p-4 rounded-lg max-h-48 overflow-y-auto">
          <li v-for="(error, index) in results.errors" :key="index" class="text-sm text-amber-700 mb-1">
            {{ error }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
