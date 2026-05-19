import DefaultTheme from 'vitepress/theme'
import CatalogBrowser from './components/CatalogBrowser.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('CatalogBrowser', CatalogBrowser)
  },
}
