# Adicionar uma camada manualmente

O botão **+ Add Layer** (barra de ferramentas do *Layer Catalog*) abre um formulário para inserir no catálogo uma camada que não está no catálogo embarcado e que não vem de uma importação WMS.

As camadas adicionadas por esse caminho carregam a origem **`manual`**: nunca são tocadas pelas atualizações do catálogo embarcado e permanecem no catálogo enquanto você não as remover.

## Campos

| Campo              | Obrigatório | Descrição                                                                |
|--------------------|:-----------:|--------------------------------------------------------------------------|
| **Category**       | ✔           | Título da categoria. Cria a categoria se ela não existir, caso contrário anexa a nova camada. |
| **Subcategory**    | ✔           | Idem no nível da subcategoria.                                            |
| **Title**          |             | Rótulo exibido. Se vazio, o identificador WMS da camada é usado.          |
| **WMS Layer Name** | ✔           | Identificador exato da camada como aparece no GetCapabilities WMS (parâmetro `LAYERS`). |
| **WMS Base URL**   | ✔           | URL base do serviço WMS, sem parâmetros de consulta.                      |
| **Source**         |             | Produtor / organismo de origem dos dados. Copiado para `Metadata`.        |
| **Resolution**     |             | Resolução espacial (`1km`, `0.05deg`, etc.). Copiada para `Metadata`.     |

Clique em **Add**: a entrada é criada imediatamente com status `pending_add` 🟠. Aparece na árvore sob a categoria e subcategoria indicadas.

## Próximo passo

Clique em **Synchronize with Climweb** para provisionar de fato a camada.

## Modificar ou remover uma camada adicionada

Uma camada `manual` é gerenciada como qualquer outra entrada do catálogo:

- **Desativá-la** (desmarcá-la) a marcará como `pending_remove`; a próxima sincronia removerá o `Dataset` do lado do Climweb.
- **Reativá-la** volta para `pending_add`; a próxima sincronia a recriará.

Para alterar a URL ou os parâmetros, o mais simples é desativar a antiga e adicionar uma nova. A edição fina de um `Dataset` provisionado se faz diretamente na administração do Wagtail (mas será considerada *local drift* — veja [Atualizações](./updates)).
