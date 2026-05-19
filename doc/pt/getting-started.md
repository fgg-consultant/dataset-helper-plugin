# Primeiros passos

Esta página descreve o percurso mínimo para fazer aparecer um primeiro conjunto de camadas WMS no mapviewer do Climweb usando o plugin Dataset Helper.

## 1. Abrir a página Dataset helper

Na administração do Wagtail, abra o menu **GeoManager → Dataset helper**.

No primeiro lançamento, a árvore central está vazia: o plugin sabe que existe um catálogo padrão em disco mas ainda não o carregou na base de dados. Uma faixa informativa o lembra no topo da página.

## 2. Preencher as configurações obrigatórias

Antes de poder carregar o catálogo embarcado, abra o painel **Settings** (recolhido logo abaixo dos contadores). No mínimo:

- **Country** *(obrigatório)* — escolha o país alvo. Esta informação serve para substituir os marcadores `{country_alpha3}` / `{country_alpha2}` nas URLs das camadas, e para preencher o enquadramento inicial do mapa (bbox vinda do Nominatim).
- **Language** — idioma no qual os títulos e descrições serão importados (`en`, `fr`, `es`, `pt`, `ar`).

Opcionais conforme os provedores que quiser ativar:

- **ECMWF Token** — necessário para as camadas `eccharts.ecmwf.int` privadas (aquelas cuja URL contém `token={ECMWF_TOKEN}`). Sem token, essas camadas são simplesmente ignoradas no carregamento.
- **Local eStation URL** — se preenchida, somente os produtos eStation efetivamente disponíveis na sua instância local serão importados. Deixe em branco para importar tudo.

Clique em **Save Settings**. Enquanto `Country` não estiver definido, o painel exibe um aviso.

Veja [Configurações](./settings) para os detalhes.

## 3. Carregar o catálogo embarcado

Clique em **Load Config JSON** e depois em **Review embedded catalog**. O plugin calcula um *changeset* sem escrever nada e mostra:

- o que será **adicionado** ao catálogo,
- o que será **atualizado**,
- o que será **removido** (se você havia carregado uma versão anterior).

Clique em **Apply changes** para validar. A árvore se preenche, e todas as entradas passam por padrão para `pending_add` (ponto laranja).

Nesta etapa, **ainda não foi criado nenhum objeto Climweb**: o catálogo só é preenchido do lado do plugin.

## 4. Refinar a seleção

Na árvore:

- Desmarque as categorias, subcategorias ou camadas que não quiser no Climweb.
- Todas as caixas vêm marcadas por padrão.
- Você pode expandir / recolher tudo pelos chevrões no topo da árvore.

Veja [O catálogo de camadas](./catalog).

## 5. Sincronizar com o Climweb

Clique em **Synchronize with Climweb**. O plugin:

- cria os `Category`, `SubCategory`, `Dataset`, `Metadata` e `WmsLayer` correspondentes às entradas marcadas,
- remove aqueles que correspondem a entradas desmarcadas mas ainda presentes na base.

Quando a sincronia termina, as entradas passam para `synced` (ponto verde). As camadas ficam então visíveis no mapviewer do Climweb.

Veja [Sincronizar com o Climweb](./sync).

## E depois?

- [Adicionar manualmente uma camada](./add-layer) que não está no catálogo.
- [Importar todas as camadas de um servidor WMS](./import-wms).
- [Carregar outro arquivo JSON](./load-config) (outro provedor, catálogo próprio…).
- Mais tarde, quando uma nova versão do plugin entregar um catálogo atualizado, veja [Atualizações do catálogo](./updates).
