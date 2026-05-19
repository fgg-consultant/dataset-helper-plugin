# Importar de um WMS

O botão **Import from WMS** permite consultar um servidor WMS remoto e pegar uma camada do seu `GetCapabilities`. É mais rápido do que preencher manualmente a URL e o identificador: o plugin lê os metadados diretamente do provedor.

As camadas importadas por esse caminho carregam a origem **`wms_import`**: nunca são tocadas pelas atualizações do catálogo embarcado.

## O fluxo em três etapas

### 1. Informar a URL do WMS

Digite a URL base do serviço (ex.: `https://example.org/wms`). O plugin constrói automaticamente a URL `GetCapabilities` (`?service=WMS&request=GetCapabilities&version=1.3.0`).

Clique em **Fetch Layers**.

### 2. Escolher uma camada

O plugin lista todas as camadas retornadas pelo servidor, com:

- o identificador (`name`),
- o título humano (`title`),
- o abstract,
- a bbox WGS84 quando exposta.

Um campo de busca filtra a lista por nome / título / abstract. Clique em uma linha para selecioná-la.

::: tip
Se você digitou a URL errada, o link *Change URL* ao lado do contador de camadas o leva de volta à etapa 1 sem recarregar a página.
:::

### 3. Configurar a camada escolhida

Aparece um pequeno formulário verde com:

| Campo            | Descrição                                                                 |
|------------------|---------------------------------------------------------------------------|
| **Layer Name**   | Pré-preenchido, somente leitura. É o identificador como retornado pelo WMS. |
| **Title**        | Pré-preenchido com o título do WMS. Editável.                              |
| **Category** *   | Categoria sob a qual a camada será classificada. Criada se não existir.    |
| **Subcategory** *| Idem.                                                                       |
| **Description**  | Pré-preenchido a partir do abstract do WMS. Serve como resumo / metadata.  |

Clique em **Add to Catalog**: a entrada é criada com status `pending_add` 🟠 e aparece na árvore.

O botão **Back to list** o leva de volta à lista de camadas do mesmo servidor — prático para importar várias camadas do mesmo provedor em sequência.

## Próximo passo

Como sempre, clique em **Synchronize with Climweb** para provisionar de fato a camada.

## Limites

- O plugin só suporta **WMS 1.3.0**. Se o servidor expõe apenas versões mais antigas, a chamada pode falhar.
- Os **estilos** e **CRS** disponíveis do lado do servidor não são expostos no formulário (somente o CRS padrão do plugin, `EPSG:3857`, é usado para as requisições Climweb).
- O formulário cria **uma camada por vez**. Para uma importação em massa do mesmo servidor, prefira preparar um arquivo JSON e usar o botão [Load Config JSON](./load-config).
