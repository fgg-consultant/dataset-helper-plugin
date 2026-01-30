<script setup lang="ts">
import { ref } from 'vue'
import EndpointSelector from '@/components/EndpointSelector.vue'
import BulkImport from '@/components/BulkImport.vue'

const activeTab = ref<'wms-wizard' | 'bulk-import'>('wms-wizard')
</script>

<template>
  <header></header>

  <main class="p-12">
    <!-- Tab Navigation -->
    <div class="flex gap-0 mb-0 border-b-2 border-gray-200">
      <button
        @click="activeTab = 'wms-wizard'"
        class="px-6 py-3 font-medium text-sm transition-all border-b-2 -mb-0.5"
        :class="
          activeTab === 'wms-wizard'
            ? 'text-emerald-600 border-emerald-600'
            : 'text-gray-500 border-transparent hover:text-gray-700 hover:bg-gray-50'
        "
      >
        WMS Wizard
      </button>
      <button
        @click="activeTab = 'bulk-import'"
        class="px-6 py-3 font-medium text-sm transition-all border-b-2 -mb-0.5"
        :class="
          activeTab === 'bulk-import'
            ? 'text-emerald-600 border-emerald-600'
            : 'text-gray-500 border-transparent hover:text-gray-700 hover:bg-gray-50'
        "
      >
        Bulk Import
      </button>
    </div>

    <!-- Tab Content -->
    <div class="py-6">
      <EndpointSelector v-if="activeTab === 'wms-wizard'" />
      <BulkImport v-else-if="activeTab === 'bulk-import'" />
    </div>
  </main>
</template>

<style scoped></style>
