# Atualizações do catálogo

O plugin embarca um arquivo `catalog.json` que descreve as camadas entregues por padrão. Esse arquivo carrega uma `version` (por exemplo `2026.05.18`). Quando uma nova versão do plugin é implantada, essa versão muda, e o plugin então sabe que há uma **atualização do catálogo** disponível.

## A faixa de atualização

Quando a versão em disco difere da versão carregada, uma faixa aparece no topo da aba *Layer Catalog*:

> A new catalog version is available — vX.  *(com um resumo em uma linha: N new · N updated · N conflicts · N removed)*

Clicar em **Review changes** abre a pré-visualização; **Later** dispensa a faixa pela sessão. **Nada é escrito na base de dados** nessa etapa.

## O changeset

A pré-visualização classifica cada entrada do novo catálogo em um **bucket** e exibe os contadores no topo:

| Bucket          | Significado                                                                                   |
|-----------------|-----------------------------------------------------------------------------------------------|
| **new**         | Entradas presentes no novo catálogo, ausentes da base.                                        |
| **updated**     | O conteúdo de origem mudou (título, URL, metadados…) e **nada foi editado manualmente** no lado do Climweb. Aplicação segura. |
| **local drift** | O conteúdo de origem está inalterado, mas o `Dataset` Climweb foi **editado manualmente** na administração do Wagtail. O plugin não tocará nele. |
| **conflict**    | O conteúdo de origem **mudou** E o `Dataset` Climweb foi editado à mão. Decisão necessária. |
| **to remove**   | Entradas de origem `config` presentes na base mas **ausentes** da nova versão do catálogo. Serão marcadas como desativadas. |
| **unchanged**   | Nada a fazer.                                                                                 |

Cada bucket é expansível e lista as entradas afetadas (título + posição na hierarquia).

## Aplicar o changeset

Até dois botões são oferecidos conforme o conteúdo do changeset:

- **Apply — keep N local edits** *(padrão quando há conflitos)* — aplica todas as mudanças **exceto** os conflitos. As modificações feitas à mão na administração do Wagtail são preservadas; as entradas em conflito permanecem em `local drift` até sua próxima decisão.
- **Apply — overwrite N conflicts** — aplica tudo, incluindo os conflitos. As modificações manuais são **sobrescritas** pelo conteúdo do catálogo.
- **Cancel** — fecha a pré-visualização, não faz nada.

Se **não há conflitos**, basta um único botão **Apply changes**.

::: tip
A pré-visualização é estritamente somente leitura. Você pode abri-la, fechá-la e reabri-la quantas vezes for necessário, sem risco.
:::

## O que a aplicação realmente faz

Aplicar o changeset atualiza a tabela `CatalogEntry` (e `CatalogState` para memorizar a nova versão carregada). **Não provisiona** os novos datasets nem remove os datasets Climweb existentes — essa é a responsabilidade de **Synchronize with Climweb**:

```
1. Review changes   → atualiza o catálogo do plugin (CatalogEntry)
2. Synchronize      → propaga a seleção para o Climweb (Dataset)
```

Concretamente, depois de um *Apply*:

- as entradas **new** aparecem como `pending_add` 🟠 na árvore,
- as entradas **updated** continuam em `synced` 🟢 mas seu conteúdo de origem é atualizado — a próxima sincronia re-provisionará o `Dataset`,
- as entradas **to remove** passam para `pending_remove` 🔴 — a próxima sincronia as removerá do Climweb,
- as entradas **local drift** são deixadas como estão (suas edições manuais permanecem até você clicar em `overwrite`).

## Quando clicar em Synchronize?

Logo após *Apply*. Sem sincronia, o Climweb continua servindo o conteúdo antigo para as camadas afetadas.
