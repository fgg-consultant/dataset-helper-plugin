# O catálogo de camadas

A aba **Layer Catalog** é a tela principal do plugin. Exibe a árvore de camadas **Category › SubCategory › Layer** e permite pilotar o que será provisionado no Climweb.

## Contadores

No topo da página, três contadores resumem o estado do catálogo:

- **Total Layers** — número total de `CatalogEntry`, todas as origens incluídas.
- **Enabled** — entradas marcadas (que estarão ou já estão no Climweb).
- **Synced** — entradas efetivamente provisionadas no Climweb.

A diferença entre *Enabled* e *Synced* é o que será modificado na próxima sincronia.

## Status de uma camada

Cada linha de camada exibe um ponto colorido:

| Ponto | Status            | Significado                                                        |
|-------|-------------------|--------------------------------------------------------------------|
| 🟢    | `synced`           | Marcada e provisionada no Climweb.                                |
| 🟠    | `pending_add`      | Marcada mas ainda não provisionada.                               |
| 🔴    | `pending_remove`   | Desmarcada mas ainda presente no Climweb.                         |
| ⚪    | `disabled`         | Desmarcada e ausente do Climweb.                                   |

Somente **Synchronize with Climweb** resolve os estados laranja e vermelho.

## Navegar pela árvore

A árvore é totalmente recolhível. Três interações principais:

- Clicar no cabeçalho de uma **categoria** ou **subcategoria** a expande / recolhe.
- Os botões ▼ e ▶ acima da árvore expandem ou recolhem **tudo**.
- Clicar na linha de uma camada abre / fecha seu **painel de detalhes** (URL WMS, identificador de camada, metadados de origem…).

## Marcar / desmarcar

- **Uma camada**: a caixa à esquerda do título ativa ou desativa essa entrada.
- **Uma subcategoria**: a caixa em seu cabeçalho alterna **todas as camadas** da subcategoria de uma vez (bulk toggle).
- **Uma categoria**: idem, mas no conjunto da categoria.

O efeito é imediato do lado do plugin (o status passa para `pending_add`/`pending_remove`) mas **nada é escrito ainda do lado do Climweb**. É preciso clicar em **Synchronize with Climweb**.

## Origem de uma camada

Cada entrada carrega uma **origem** que descreve como chegou ao catálogo:

| Origem       | Como apareceu                                                              |
|--------------|----------------------------------------------------------------------------|
| `config`     | Carregada do catálogo JSON embarcado (ou de um JSON importado manualmente). |
| `manual`     | Adicionada pelo formulário *+ Add Layer*.                                  |
| `wms_import` | Importada de um GetCapabilities WMS remoto.                                |

A origem importa sobretudo para as **atualizações** do catálogo embarcado: somente as entradas `config` podem ser marcadas como `to_remove` quando desaparecem de uma nova versão do JSON. As entradas `manual` e `wms_import` nunca são tocadas pelas atualizações automáticas.

## Ações da barra de ferramentas

Sob o painel de configurações, a barra de ferramentas reúne as ações principais:

- **Synchronize with Climweb** — aplica a seleção atual (veja [Sincronizar](./sync)).
- **Load embedded catalog** — previsualiza e aplica o catálogo embarcado com o plugin (veja [Atualizações](./updates)).
- **Reset Catalog** — operação **destrutiva**; veja [Zona perigosa](./danger-zone).
