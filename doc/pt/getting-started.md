# Primeiros passos

Esta página descreve o percurso mínimo para fazer aparecer um primeiro conjunto de camadas WMS no mapviewer do Climweb usando o plugin Dataset Helper.

## Instalar o plugin no Climweb

Antes de usar o plugin a partir da administração do Wagtail, ele precisa estar instalado do lado do Climweb. Edite o arquivo `.env` da sua instância do Climweb:

1. Atualize o Climweb para a versão compatível:
   ```ini
   CLIMWEB_VERSION=1.1.3
   ```
2. Declare o repositório do plugin:
   ```ini
   CLIMWEB_PLUGIN_GIT_REPOS=https://github.com/fgg-consultant/dataset-helper-plugin
   ```

Em seguida, reinicie o Climweb para que o plugin declarado seja baixado e instalado:

```bash
docker compose down
docker compose up -d
```

Para o procedimento completo e as opções avançadas (vários plugins, branch/tag específica, plugins privados…), consulte a [documentação oficial do Climweb](https://climweb.readthedocs.io/en/v1.1.1/_docs/technical/extending-climweb/plugin-installation.html).

## 1. Abrir a página Dataset helper

Na administração do Wagtail, abra **GeoManager → Dataset helper**.

No primeiro lançamento, a árvore central está vazia: o plugin sabe que existe um catálogo padrão em disco mas ainda não o carregou na base de dados. Uma faixa no topo da página o lembra disso.

## 2. Preencher as configurações obrigatórias

Antes de carregar o catálogo embarcado, vá para a aba **Settings** — a primeira, que abre automaticamente em uma instância nova (as outras abas ficam bloqueadas até você terminar aqui). No mínimo:

- **Country** *(obrigatório)* — escolha o país alvo. Esta informação serve para substituir os marcadores `{country_alpha3}` / `{country_alpha2}` nas URLs das camadas e para definir o enquadramento inicial do mapa (bbox vinda do Nominatim).
- **Language** — idioma no qual os títulos e descrições serão importados (`en`, `fr`, `es`, `pt`, `ar`).

Opcionais, conforme os provedores que quiser ativar:

- **ECMWF Token** — necessário para as camadas privadas `eccharts.ecmwf.int` (aquelas cuja URL contém `token={ECMWF_TOKEN}`). Sem token, essas camadas são simplesmente ignoradas no carregamento.
- **Local eStation URL** — se preenchida, somente os produtos eStation efetivamente disponíveis na sua instância local serão importados. Deixe em branco para importar tudo.

Clique em **Save Settings**. Enquanto `Country` não estiver definido, as outras abas ficam bloqueadas; depois de salvo, a aba Settings as desbloqueia e oferece atalhos para o catálogo e os limites.

Veja [Configurações](./settings) para os detalhes.

## 3. Carregar o catálogo embarcado

Enquanto o catálogo está vazio, a aba exibe um único bloco de aviso — *No catalog loaded yet* — com um botão **Load catalog**. Clique nele: como o catálogo local está vazio, o catálogo embarcado é **aplicado diretamente** (sem necessidade de pré-visualização — não há nada com que conflitar).

A árvore se preenche e todas as entradas passam por padrão para `pending_add` (ponto laranja).

Nesta etapa, **ainda não foi criado nenhum objeto Climweb**: o catálogo só foi preenchido do lado do plugin.

::: tip
A etapa de pré-visualização/diff só é usada **mais tarde**, para as *atualizações*: quando uma versão mais recente do catálogo é entregue, uma faixa permite revisar o changeset antes de aplicá-lo. Veja [Atualizações do catálogo](./updates).
:::

## 4. Refinar a seleção

Na árvore:

- Desmarque as categorias, subcategorias ou camadas que não quiser no Climweb.
- Todas as caixas vêm marcadas por padrão.
- Você pode recolher / expandir toda a árvore pelos chevrões acima dela.

Veja [O catálogo de camadas](./catalog).

## 5. Sincronizar com o Climweb

Assim que sua seleção difere do Climweb, uma **faixa de dessincronização** aparece abaixo da visão geral, resumindo o que está pendente. Clique no seu botão **Synchronize with Climweb**. O plugin:

- cria os objetos `Category`, `SubCategory`, `Dataset`, `Metadata` e `WmsLayer` correspondentes às entradas marcadas,
- remove aqueles que correspondem a entradas que você desmarcou mas ainda estavam na base.

Quando a sincronia termina, as entradas passam para `synced` (ponto verde). As camadas ficam então visíveis no mapviewer do Climweb.

Veja [Sincronizar com o Climweb](./sync).

## E depois?

- Mais tarde, quando uma nova versão do plugin entregar um catálogo atualizado, veja [Atualizações do catálogo](./updates).
