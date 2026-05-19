import { defineConfig } from 'vitepress'

// Set DOCS_BASE when deploying to a subpath (e.g. GitHub Pages project site).
// Default base path matches the GitHub repository name.
const base = process.env.DOCS_BASE ?? '/dataset-helper-plugin/'

const GITHUB_URL = 'https://github.com/fgg-consultant/dataset-helper-plugin'
const EDIT_PATTERN = `${GITHUB_URL}/edit/main/doc/:path`

// ─── Sidebars per locale ───────────────────────────────────────────────────

function sidebarFr() {
  return [
    {
      text: 'Introduction',
      items: [
        { text: 'Vue d\'ensemble', link: '/' },
        { text: 'Premiers pas', link: '/getting-started' },
        { text: 'Réglages', link: '/settings' },
      ],
    },
    {
      text: 'Utilisation quotidienne',
      items: [
        { text: 'Le catalogue de couches', link: '/catalog' },
        { text: 'Explorer le catalogue embarqué', link: '/catalog-browser' },
        { text: 'Synchroniser avec Climweb', link: '/sync' },
        { text: 'Mises à jour du catalogue', link: '/updates' },
      ],
    },
    {
      text: 'Étendre le catalogue',
      items: [
        { text: 'Ajouter une couche', link: '/add-layer' },
        { text: 'Importer depuis un WMS', link: '/import-wms' },
        { text: 'Charger un fichier JSON', link: '/load-config' },
      ],
    },
    {
      text: 'Administration',
      items: [{ text: 'Zone dangereuse', link: '/danger-zone' }],
    },
  ]
}

function sidebarEn() {
  return [
    {
      text: 'Introduction',
      items: [
        { text: 'Overview', link: '/en/' },
        { text: 'Getting started', link: '/en/getting-started' },
        { text: 'Settings', link: '/en/settings' },
      ],
    },
    {
      text: 'Daily use',
      items: [
        { text: 'The layer catalog', link: '/en/catalog' },
        { text: 'Embedded catalog browser', link: '/en/catalog-browser' },
        { text: 'Synchronize with Climweb', link: '/en/sync' },
        { text: 'Catalog updates', link: '/en/updates' },
      ],
    },
    {
      text: 'Extending the catalog',
      items: [
        { text: 'Add a layer', link: '/en/add-layer' },
        { text: 'Import from a WMS', link: '/en/import-wms' },
        { text: 'Load a JSON file', link: '/en/load-config' },
      ],
    },
    {
      text: 'Administration',
      items: [{ text: 'Danger zone', link: '/en/danger-zone' }],
    },
  ]
}

function sidebarEs() {
  return [
    {
      text: 'Introducción',
      items: [
        { text: 'Visión general', link: '/es/' },
        { text: 'Primeros pasos', link: '/es/getting-started' },
        { text: 'Configuración', link: '/es/settings' },
      ],
    },
    {
      text: 'Uso diario',
      items: [
        { text: 'El catálogo de capas', link: '/es/catalog' },
        { text: 'Explorar el catálogo incluido', link: '/es/catalog-browser' },
        { text: 'Sincronizar con Climweb', link: '/es/sync' },
        { text: 'Actualizaciones del catálogo', link: '/es/updates' },
      ],
    },
    {
      text: 'Ampliar el catálogo',
      items: [
        { text: 'Añadir una capa', link: '/es/add-layer' },
        { text: 'Importar desde un WMS', link: '/es/import-wms' },
        { text: 'Cargar un archivo JSON', link: '/es/load-config' },
      ],
    },
    {
      text: 'Administración',
      items: [{ text: 'Zona peligrosa', link: '/es/danger-zone' }],
    },
  ]
}

function sidebarPt() {
  return [
    {
      text: 'Introdução',
      items: [
        { text: 'Visão geral', link: '/pt/' },
        { text: 'Primeiros passos', link: '/pt/getting-started' },
        { text: 'Configurações', link: '/pt/settings' },
      ],
    },
    {
      text: 'Uso diário',
      items: [
        { text: 'O catálogo de camadas', link: '/pt/catalog' },
        { text: 'Explorar o catálogo embarcado', link: '/pt/catalog-browser' },
        { text: 'Sincronizar com Climweb', link: '/pt/sync' },
        { text: 'Atualizações do catálogo', link: '/pt/updates' },
      ],
    },
    {
      text: 'Ampliar o catálogo',
      items: [
        { text: 'Adicionar uma camada', link: '/pt/add-layer' },
        { text: 'Importar de um WMS', link: '/pt/import-wms' },
        { text: 'Carregar um arquivo JSON', link: '/pt/load-config' },
      ],
    },
    {
      text: 'Administração',
      items: [{ text: 'Zona perigosa', link: '/pt/danger-zone' }],
    },
  ]
}

function sidebarAr() {
  return [
    {
      text: 'مقدمة',
      items: [
        { text: 'نظرة عامة', link: '/ar/' },
        { text: 'البدء السريع', link: '/ar/getting-started' },
        { text: 'الإعدادات', link: '/ar/settings' },
      ],
    },
    {
      text: 'الاستخدام اليومي',
      items: [
        { text: 'كتالوج الطبقات', link: '/ar/catalog' },
        { text: 'استعراض الكتالوج المدمج', link: '/ar/catalog-browser' },
        { text: 'المزامنة مع Climweb', link: '/ar/sync' },
        { text: 'تحديثات الكتالوج', link: '/ar/updates' },
      ],
    },
    {
      text: 'توسيع الكتالوج',
      items: [
        { text: 'إضافة طبقة', link: '/ar/add-layer' },
        { text: 'الاستيراد من WMS', link: '/ar/import-wms' },
        { text: 'تحميل ملف JSON', link: '/ar/load-config' },
      ],
    },
    {
      text: 'الإدارة',
      items: [{ text: 'المنطقة الخطرة', link: '/ar/danger-zone' }],
    },
  ]
}

// ─── Locales ───────────────────────────────────────────────────────────────

const locales = {
  root: {
    label: 'Français',
    lang: 'fr-FR',
    title: 'Dataset Helper',
    description:
      'Documentation utilisateur du plugin Climweb Dataset Helper',
    themeConfig: {
      nav: [
        { text: 'Guide', link: '/getting-started' },
        { text: 'Catalogue', link: '/catalog' },
        { text: 'Synchro', link: '/sync' },
      ],
      sidebar: sidebarFr(),
      docFooter: { prev: 'Page précédente', next: 'Page suivante' },
      outline: { label: 'Sur cette page', level: [2, 3] },
      lastUpdatedText: 'Dernière mise à jour',
      darkModeSwitchLabel: 'Apparence',
      sidebarMenuLabel: 'Menu',
      returnToTopLabel: 'Retour en haut',
      editLink: {
        pattern: EDIT_PATTERN,
        text: 'Modifier cette page sur GitHub',
      },
      footer: {
        message: 'Dataset Helper — plugin Climweb',
        copyright: 'MIT License',
      },
      search: {
        provider: 'local',
        options: {
          translations: {
            button: {
              buttonText: 'Rechercher',
              buttonAriaLabel: 'Rechercher dans la documentation',
            },
            modal: {
              noResultsText: 'Aucun résultat pour',
              resetButtonTitle: 'Réinitialiser la recherche',
              footer: {
                selectText: 'pour sélectionner',
                navigateText: 'pour naviguer',
                closeText: 'pour fermer',
              },
            },
          },
        },
      },
    },
  },

  en: {
    label: 'English',
    lang: 'en-US',
    link: '/en/',
    title: 'Dataset Helper',
    description: 'User documentation for the Climweb Dataset Helper plugin',
    themeConfig: {
      nav: [
        { text: 'Guide', link: '/en/getting-started' },
        { text: 'Catalog', link: '/en/catalog' },
        { text: 'Sync', link: '/en/sync' },
      ],
      sidebar: sidebarEn(),
      docFooter: { prev: 'Previous page', next: 'Next page' },
      outline: { label: 'On this page', level: [2, 3] },
      lastUpdatedText: 'Last updated',
      darkModeSwitchLabel: 'Appearance',
      sidebarMenuLabel: 'Menu',
      returnToTopLabel: 'Return to top',
      editLink: {
        pattern: EDIT_PATTERN,
        text: 'Edit this page on GitHub',
      },
      footer: {
        message: 'Dataset Helper — Climweb plugin',
        copyright: 'MIT License',
      },
    },
  },

  es: {
    label: 'Español',
    lang: 'es-ES',
    link: '/es/',
    title: 'Dataset Helper',
    description:
      'Documentación de usuario del plugin Climweb Dataset Helper',
    themeConfig: {
      nav: [
        { text: 'Guía', link: '/es/getting-started' },
        { text: 'Catálogo', link: '/es/catalog' },
        { text: 'Sincro', link: '/es/sync' },
      ],
      sidebar: sidebarEs(),
      docFooter: { prev: 'Página anterior', next: 'Página siguiente' },
      outline: { label: 'En esta página', level: [2, 3] },
      lastUpdatedText: 'Última actualización',
      darkModeSwitchLabel: 'Apariencia',
      sidebarMenuLabel: 'Menú',
      returnToTopLabel: 'Volver arriba',
      editLink: {
        pattern: EDIT_PATTERN,
        text: 'Editar esta página en GitHub',
      },
      footer: {
        message: 'Dataset Helper — plugin Climweb',
        copyright: 'MIT License',
      },
    },
  },

  pt: {
    label: 'Português',
    lang: 'pt-BR',
    link: '/pt/',
    title: 'Dataset Helper',
    description:
      'Documentação do usuário do plugin Climweb Dataset Helper',
    themeConfig: {
      nav: [
        { text: 'Guia', link: '/pt/getting-started' },
        { text: 'Catálogo', link: '/pt/catalog' },
        { text: 'Sincronia', link: '/pt/sync' },
      ],
      sidebar: sidebarPt(),
      docFooter: { prev: 'Página anterior', next: 'Próxima página' },
      outline: { label: 'Nesta página', level: [2, 3] },
      lastUpdatedText: 'Última atualização',
      darkModeSwitchLabel: 'Aparência',
      sidebarMenuLabel: 'Menu',
      returnToTopLabel: 'Voltar ao topo',
      editLink: {
        pattern: EDIT_PATTERN,
        text: 'Editar esta página no GitHub',
      },
      footer: {
        message: 'Dataset Helper — plugin Climweb',
        copyright: 'MIT License',
      },
    },
  },

  ar: {
    label: 'العربية',
    lang: 'ar',
    dir: 'rtl',
    link: '/ar/',
    title: 'Dataset Helper',
    description: 'دليل المستخدم لمكوّن Climweb Dataset Helper',
    themeConfig: {
      nav: [
        { text: 'الدليل', link: '/ar/getting-started' },
        { text: 'الكتالوج', link: '/ar/catalog' },
        { text: 'المزامنة', link: '/ar/sync' },
      ],
      sidebar: sidebarAr(),
      docFooter: { prev: 'الصفحة السابقة', next: 'الصفحة التالية' },
      outline: { label: 'في هذه الصفحة', level: [2, 3] },
      lastUpdatedText: 'آخر تحديث',
      darkModeSwitchLabel: 'المظهر',
      sidebarMenuLabel: 'القائمة',
      returnToTopLabel: 'العودة إلى الأعلى',
      editLink: {
        pattern: EDIT_PATTERN,
        text: 'تعديل هذه الصفحة على GitHub',
      },
      footer: {
        message: 'Dataset Helper — مكوّن Climweb',
        copyright: 'MIT License',
      },
    },
  },
}

export default defineConfig({
  base,
  lastUpdated: true,
  cleanUrls: true,

  head: [['meta', { name: 'theme-color', content: '#059669' }]],

  // VitePress reads title/description/lang from the root locale.
  title: 'Dataset Helper',
  description:
    'Documentation utilisateur du plugin Climweb Dataset Helper',

  locales,

  themeConfig: {
    socialLinks: [{ icon: 'github', link: GITHUB_URL }],
    search: {
      provider: 'local',
      options: {
        locales: {
          es: {
            translations: {
              button: {
                buttonText: 'Buscar',
                buttonAriaLabel: 'Buscar en la documentación',
              },
              modal: {
                noResultsText: 'Sin resultados para',
                resetButtonTitle: 'Restablecer búsqueda',
                footer: {
                  selectText: 'para seleccionar',
                  navigateText: 'para navegar',
                  closeText: 'para cerrar',
                },
              },
            },
          },
          pt: {
            translations: {
              button: {
                buttonText: 'Buscar',
                buttonAriaLabel: 'Buscar na documentação',
              },
              modal: {
                noResultsText: 'Sem resultados para',
                resetButtonTitle: 'Limpar busca',
                footer: {
                  selectText: 'para selecionar',
                  navigateText: 'para navegar',
                  closeText: 'para fechar',
                },
              },
            },
          },
          ar: {
            translations: {
              button: {
                buttonText: 'بحث',
                buttonAriaLabel: 'البحث في الوثائق',
              },
              modal: {
                noResultsText: 'لا توجد نتائج لـ',
                resetButtonTitle: 'إعادة ضبط البحث',
                footer: {
                  selectText: 'للاختيار',
                  navigateText: 'للتنقل',
                  closeText: 'للإغلاق',
                },
              },
            },
          },
          root: {
            translations: {
              button: {
                buttonText: 'Rechercher',
                buttonAriaLabel: 'Rechercher dans la documentation',
              },
              modal: {
                noResultsText: 'Aucun résultat pour',
                resetButtonTitle: 'Réinitialiser la recherche',
                footer: {
                  selectText: 'pour sélectionner',
                  navigateText: 'pour naviguer',
                  closeText: 'pour fermer',
                },
              },
            },
          },
        },
      },
    },
  },
})
