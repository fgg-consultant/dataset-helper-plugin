---
layout: home

hero:
  name: Dataset Helper
  text: O catálogo de camadas do Climweb
  tagline: Ative, importe e sincronize as camadas do mapviewer sem tocar na administração do Wagtail.
  actions:
    - theme: brand
      text: Primeiros passos
      link: /pt/getting-started
    - theme: alt
      text: O catálogo
      link: /pt/catalog
    - theme: alt
      text: GitHub
      link: https://github.com/fgg-consultant/dataset-helper-plugin

features:
  - icon: 📚
    title: Catálogo embarcado
    details: ~865 camadas prontas para uso (JRC eStation, ECMWF, CAMS, EUMETSAT, CGLS…) entregues com o plugin.
  - icon: ✅
    title: Seleção por caixas
    details: Escolha as camadas desejadas em uma árvore Categoria › Subcategoria › Camada. Ativação em massa por categoria.
  - icon: 🔄
    title: Sincronização controlada
    details: Nada é escrito no Climweb enquanto você não clica em Sincronizar. As edições manuais são detectadas e preservadas.
  - icon: ➕
    title: Catálogo extensível
    details: Adicione suas próprias camadas manualmente, importe a partir de um GetCapabilities WMS remoto ou carregue um JSON personalizado.
---

## Visão geral

O **Dataset Helper** é um plugin Climweb que ajuda os administradores a construir o catálogo de camadas do mapviewer sem precisar criar manualmente cada `Dataset`, `Category`, `SubCategory` e `WmsLayer` na administração do Wagtail.

O plugin embarca um catálogo padrão e fornece uma interface para:

- ativar ou desativar camadas com um simples clique em uma caixa,
- **sincronizar** a seleção com a base de dados do Climweb (criação / remoção dos `Dataset` correspondentes),
- **enriquecer** o catálogo com camadas adicionadas manualmente, importadas de um WMS remoto ou carregadas de um arquivo JSON,
- acompanhar as **atualizações** do catálogo embarcado quando uma nova versão é entregue com o plugin.

## Onde encontrar o plugin

Na administração do Wagtail, abra o menu **GeoManager → Dataset helper**. A página se divide em duas abas:

- **Layer Catalog** — a tela principal de trabalho (configurações, árvore de camadas, ações de sincronização e importação).
- **Danger Zone** — as operações destrutivas (purga dos dados provisionados, limpeza completa).

## Modelo mental

O plugin mantém seu próprio catálogo (`CatalogEntry`) **ao lado** dos objetos do Climweb. Nada é escrito no Climweb enquanto você não clica em **Synchronize with Climweb**.

```
Catálogo (CatalogEntry)             Climweb (geomanager)
─────────────────────────           ───────────────────────────
Entry  enabled=true   ──┐
Entry  enabled=true   ──┼── Sync ──►  Category › SubCategory › Dataset › WmsLayer
Entry  enabled=false  ──┘
```

Cada entrada tem um **estado** que resume sua relação com o Climweb:

| Ponto | Estado            | Significado                                                            |
|-------|-------------------|------------------------------------------------------------------------|
| 🟢    | `synced`           | Marcada e já provisionada no Climweb.                                 |
| 🟠    | `pending_add`      | Marcada mas ainda não provisionada — será criada na próxima sincronia. |
| 🔴    | `pending_remove`   | Desmarcada mas ainda presente no Climweb — será removida.             |
| ⚪    | `disabled`         | Desmarcada e ausente do Climweb — nada a fazer.                        |

## Por onde começar

Se for sua primeira vez, siga o [percurso em 5 passos](./getting-started). Caso contrário, navegue pela barra lateral ou use a busca no canto superior direito.
