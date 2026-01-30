<script setup lang="ts">
import { searchPatternInLayers } from '@/service/search.helper.ts'
import { ref, computed, shallowRef } from 'vue'
import IconInfoCircle from '@/__icons/IconInfoCircle.vue'
import IconX from '@/__icons/IconX.vue'
import IconLoader2 from '@/__icons/IconLoader2.vue'
import IconSearch from '@/__icons/IconSearch.vue'
import { WmsEndpoint } from '@camptocamp/ogc-client'

const searchPattern = ref('')
const layerInfo = ref<any>(null)
const loading = ref(false)
const checkedLayers = ref<string[]>([])
const endpointUrl = ref('')
const endpoint = shallowRef<WmsEndpoint | null>(null)

async function selectEndpoint(event: Event) {
  const url = (event.target as HTMLInputElement).value
  endpointUrl.value = url
  loading.value = true
  endpoint.value = await new WmsEndpoint(endpointUrl.value).isReady()
  loading.value = false
}

const layers = computed(() =>
  endpoint.value?.getFlattenedLayers().sort((a, b) => a.title.localeCompare(b.title)),
)

const filteredLayers = computed(() =>
  layers.value ? searchPatternInLayers(layers.value, searchPattern.value) : [],
)

const wmsImageUrl = computed(() => {
  if (!endpointUrl.value || !layerInfo.value) return null
  return endpoint.value!.getMapUrl([layerInfo.value.name], {
    widthPx: 256,
    heightPx: 200,
    extent: [-4554203.020722416, -4917533.4489256255, 8081548.881484727, 4906985.59447665],
    outputFormat: 'image/png',
    crs: 'EPSG:3857',
  })
})

function createDatasets() {
  if (!layers.value) return
  layers.value
    .filter((layer) => checkedLayers.value.includes(layer.name))
    .forEach((layer) => {
      const dataset = {
        type: 'wms',
        name: layer.title,
        url: endpointUrl.value,
        layer: layer,
        params: {
          format: 'image/png',
          transparent: true,
        },
      }
      window.postMessage({ type: 'vue-add-dataset', dataset }, 'http://localhost')
      console.log('Creating dataset:', dataset)
    })
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <input
      type="text"
      class="input min-w-150"
      placeholder="WMS Server URL"
      list="endpoints"
      @change="selectEndpoint"
    />

    <datalist id="endpoints">
      <option value="https://estation.jrc.ec.europa.eu/eStation3/webservices">
        Climate Station Global
      </option>
      <option value="https://view.eumetsat.int/geoserver/wms">EUMETSAT</option>
      <option value="https://ada.acmad.org/geoserver/wms">ACMAD</option>
      <option value="https://ada.acmad.org/geoserver/wms">ECMWF</option>
    </datalist>

    <div v-if="loading" class="flex gap-3">
      <IconLoader2 class="animate-spin h-6 w-6"></IconLoader2>
      Loading...
    </div>

    <div class="flex gap-4" v-if="endpoint">
      <div class="border! border-gray-300! rounded! flex flex-col gap-4 w-150">
        <div class="bg-gray-200 px-5 py-3">
          <div class="font-bold text-xl">{{ endpoint.getServiceInfo().title }}</div>
          <div class="text-sm text-gray-700">{{ endpoint.getServiceInfo().abstract }}</div>
        </div>
        <div class="flex gap-4">
          <div class="px-5 relative flex w-90">
            <input
              type="text"
              class="input outline-orange-800/80 outline-offset-1"
              placeholder="Filter on layers"
              v-model="searchPattern"
            />
            <IconSearch class="h-5 w-5 absolute right-10 z-10 top-2.5 text-gray-400"></IconSearch>
          </div>
          <button
            :disabled="checkedLayers.length === 0"
            @click="createDatasets()"
            class="px-3 cursor-pointer py-2 text-white bg-emerald-600 rounded-md hover:bg-emerald-700 transition-all disabled:cursor-not-allowed disabled:bg-gray-400"
          >
            Add datasets in Climweb
          </button>
        </div>
        <div class="px-5 flex gap-3 text-emerald-600">
          {{ checkedLayers.length }} selected layers.
        </div>
        <div class="flex gap-2 mb-4 px-5">
          <div>
            <div v-for="layer in filteredLayers" :key="layer.name" class="flex gap-3">
              <label
                class="grow border! border-transparent! has-checked:bg-emerald-100! hover:text-emerald-600! gap-4 px-3 cursor-pointer flex items-center"
                :class="layerInfo?.name === layer.name ? 'border-orange-800!' : ''"
              >
                <input
                  type="checkbox"
                  v-model="checkedLayers"
                  :value="layer.name"
                  class="before:bg-none appearance-none! border! border-gray-400! cursor-pointer! w-4! h-4! rounded! checked:text-white! checked:border-emerald-500! checked:bg-emerald-500!"
                />
                <span class="truncate"> {{ layer.title }}</span>
              </label>
              <button @click="layerInfo = layer" title="Layer info">
                <IconInfoCircle
                  class="h-5 w-5 cursor-pointer hover:text-orange-700 hover:scale-110 transition-all"
                ></IconInfoCircle>
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-if="layerInfo" class="border! border-gray-300! rounded! flex flex-col gap-4 w-120">
        <div class="bg-orange-800/50 px-5 py-3">
          <div class="flex gap-2">
            <div class="grow font-bold text-xl">Layer Info</div>
            <button @click="layerInfo = null">
              <IconX class="h-5 w-5 hover:scale-115 transition-all cursor-pointer"></IconX>
            </button>
          </div>
        </div>
        <div class="px-5 flex flex-col gap-2">
          <div class="">{{ layerInfo.title }}</div>
          <div class="">
            <span class="text-sm px-2 py-1 rounded bg-gray-700 text-white">{{
              layerInfo.name
            }}</span>
          </div>
          <div class="text-sm text-gray-700">{{ layerInfo.abstract }}</div>
          <img
            :src="wmsImageUrl"
            v-if="wmsImageUrl"
            class="border border-gray-300 rounded-xl p-2"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
