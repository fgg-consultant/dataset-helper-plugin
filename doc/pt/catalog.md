# O catálogo de camadas

A aba **Layer Catalog** é a tela principal do plugin. Exibe a árvore **Category › SubCategory › Layer** e permite controlar o que será provisionado no Climweb.

No topo da aba, um cabeçalho relembra o contexto — *GeoManager · Layer catalog for the Climweb map viewer* — com um indicador que mostra a versão do catálogo atualmente carregada (ou *not loaded*) e um link para esta documentação.

## Visão geral

Um cartão no topo resume o estado do catálogo.

Três contadores:

- **Catalog layers** — número total de `CatalogEntry`, todas as origens incluídas.
- **Enabled** — entradas marcadas (que estarão ou já estão no Climweb).
- **Synced** — entradas efetivamente provisionadas no Climweb.

Em seguida, um **medidor de status** decompõe o catálogo por estado — **Synced**, **To add**, **To remove**, **Disabled** — com uma legenda colorida, para que você veja num relance o quão distante o catálogo está do Climweb.

Uma linha discreta relembra a versão carregada: *Catalog vX · loaded DATE*.

## Status de sincronização

O plugin sinaliza imediatamente se o Climweb está sincronizado com sua seleção local:

- **In sync** — nada é exibido; o Climweb reflete exatamente o seu catálogo.
- **Out of sync** — uma faixa em destaque aparece logo abaixo da visão geral: *Catalog out of sync with Climweb — N pending changes — X to create, Y to remove, Z to update*, acompanhada de um botão **Synchronize with Climweb**.

Depois de executar uma sincronia (ou um carregamento/reset), o **resultado** aparece no mesmo lugar, no mesmo estilo — verde em caso de sucesso, vermelho em caso de erro — com um **×** verde para dispensá-lo.

## Status de uma camada

Cada linha de camada exibe um ponto colorido:

| Ponto | Status              | Significado                                                      |
|-------|---------------------|------------------------------------------------------------------|
| 🟢    | `synced`             | Marcada e provisionada no Climweb.                              |
| 🟠    | `pending_add`        | Marcada mas ainda não provisionada.                             |
| 🔴    | `pending_remove`     | Desmarcada mas ainda presente no Climweb.                       |
| ⚪    | `disabled`           | Desmarcada e ausente do Climweb.                                |

Somente **Synchronize with Climweb** resolve os estados laranja e vermelho.

## Navegar pela árvore

Uma barra de controle fica acima da árvore: uma **caixa de pesquisa**, **chips de filtro por status**, botões **select-all / deselect-all** e botões para **expandir / recolher tudo**.

A árvore é totalmente recolhível. Três interações principais:

- Clicar no cabeçalho de uma **categoria** ou **subcategoria** a expande / recolhe.
- Os botões de expandir / recolher (no canto superior direito da barra de controle) abrem ou fecham **todas** as categorias e subcategorias de uma vez.
- Clicar na linha de uma camada abre / fecha seu **painel de detalhes** (nome da camada, URL do serviço, provedor, resolução, frequência, origem e as opções do Climweb — popup, legenda WMS, multitemporal, visível inicialmente, near real-time — além de uma pré-visualização GetMap).

Cada linha exibe, num relance: uma **caixa de seleção** de três estados, um **ponto de status** colorido, o **nome** da camada e **badges** para o provedor, o tipo de camada e (para entradas legadas) a origem. O cabeçalho de cada categoria também traz uma pequena **mini-barra de status** que resume suas camadas.

## Pesquisar e filtrar

A barra de controle acima da árvore permite restringir o que é exibido — puramente do lado do cliente, nada é enviado ao servidor:

- **Caixa de pesquisa** — digite para manter apenas as camadas cujo nome, identificador de camada, provedor, categoria ou subcategoria corresponda. As categorias e subcategorias correspondentes se expandem automaticamente. Limpe-a com o botão **×** ou a tecla **Esc**.
- **Chips de filtro** — **All**, **To add**, **To remove**, **Disabled** restringem a árvore às camadas naquele estado. Os chips exibem uma contagem ao vivo para cada estado pendente.

Enquanto uma pesquisa ou um filtro está ativo, somente os ramos correspondentes são exibidos e expandidos; ao limpar, a árvore volta a recolher para o seu estado anterior de expansão/recolhimento. Se nada corresponder, a árvore exibe *No layer matches your search.*

## Marcar / desmarcar

- **Uma única camada**: a caixa à esquerda do título ativa ou desativa essa entrada.
- **Uma subcategoria**: a caixa em seu cabeçalho alterna **todas as camadas** da subcategoria de uma vez (bulk toggle).
- **Uma categoria**: idem, mas no conjunto da categoria.
- **O catálogo inteiro**: os botões **select-all** / **deselect-all** na barra de controle ativam ou desativam *todas* as camadas de uma vez.

O efeito é imediato do lado do plugin (o status passa para `pending_add` / `pending_remove`) mas **nada é escrito ainda no Climweb**. A faixa de dessincronização aparece então — clique em **Synchronize with Climweb** para aplicar.

## Origem de uma camada

Cada entrada carrega uma **origem** que descreve como chegou ao catálogo:

| Origem       | Como apareceu                                                                   |
|--------------|----------------------------------------------------------------------------------|
| `config`     | Carregada do catálogo JSON embarcado. Esta é a única origem criada atualmente.  |
| `manual` / `wms_import` | Origens legadas de versões anteriores do plugin (adição manual / importação WMS). Esses fluxos foram removidos; tais entradas ainda podem existir em instâncias mais antigas. |

A origem importa sobretudo para as **atualizações** do catálogo embarcado: somente as entradas `config` podem ser marcadas como `to_remove` quando desaparecem de uma nova versão do catálogo. As entradas legadas `manual` / `wms_import` nunca são tocadas pelas atualizações automáticas.

## Catálogo vazio

Quando nenhum catálogo foi carregado ainda, a aba exibe **apenas** um bloco de aviso — *No catalog loaded yet* — com um botão **Load catalog**. Clicar nele carrega o catálogo embarcado **diretamente** (sem pré-visualização, já que não há nada com que conflitar). A visão geral e a árvore aparecem então. Veja [Primeiros passos](./getting-started).

## Barra de ferramentas

Uma vez que um catálogo está carregado, resta uma única ação na barra de ferramentas:

- **Reset Catalog** — operação **destrutiva**; veja [Zona perigosa](./danger-zone).

O carregamento e a sincronização são conduzidos pelas faixas descritas acima, em vez de por botões da barra de ferramentas:

- o botão **Load catalog** (estado vazio) ou o **Review changes** da faixa de atualização (veja [Atualizações do catálogo](./updates)) preenchem o catálogo,
- o botão **Synchronize with Climweb** (faixa de dessincronização) propaga a seleção para o Climweb (veja [Sincronizar](./sync)).
