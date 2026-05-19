# Atualizações do catálogo embarcado

O plugin embarca um arquivo `catalog.json` que descreve o conjunto de camadas entregues por padrão. Esse arquivo carrega uma `version` (por exemplo `2026.05.18`). Quando uma nova versão do plugin é implantada, essa versão muda, e o plugin então sabe que há uma **atualização do catálogo** disponível.

## A faixa de atualização

Se a versão em disco difere da versão carregada na base, uma faixa aparece no topo da aba *Layer Catalog*:

> A new catalog version is available — review changes

Clicar em **Review changes** abre a pré-visualização. **Nada é escrito ainda na base** nessa etapa.

Você também pode disparar a pré-visualização manualmente: **Load Config JSON → Review embedded catalog**.

## O changeset

A pré-visualização classifica cada entrada do novo catálogo em um **bucket** e exibe os contadores no topo:

| Bucket           | Significado                                                                                |
|------------------|---------------------------------------------------------------------------------------------|
| **new**          | Entradas presentes no novo catálogo, ausentes da base.                                     |
| **updated**      | O conteúdo de origem mudou (título, URL, metadados…) e **nada foi modificado à mão** no lado do Climweb. Aplicação segura. |
| **local drift**  | O conteúdo de origem está inalterado mas o `Dataset` Climweb foi **editado manualmente** na administração do Wagtail. O plugin não tocará em nada. |
| **conflict**     | O conteúdo de origem **mudou** E o `Dataset` Climweb foi editado à mão. Decisão necessária. |
| **to remove**    | Entradas de origem `config` presentes na base mas **ausentes** da nova versão do catálogo. Serão marcadas como desativadas. |
| **unchanged**    | Nada a fazer.                                                                              |

Cada bucket é expansível e lista as entradas afetadas (título + posição na hierarquia).

## Aplicar o changeset

Dois botões são oferecidos conforme o conteúdo do changeset:

- **Apply — keep N local edits** *(padrão quando há conflitos)* — aplica todas as mudanças **exceto** os conflitos. As modificações feitas à mão na administração do Wagtail são preservadas; as entradas em conflito permanecem em `local drift` até sua próxima decisão.
- **Apply — overwrite N conflicts** — aplica tudo, incluindo os conflitos. As modificações manuais são **sobrescritas** pelo conteúdo do catálogo.
- **Cancel** — fecha a pré-visualização, não faz nada.

Se **não há conflito**, basta um único botão **Apply changes**.

::: tip
A pré-visualização é estritamente somente leitura. Você pode abri-la, fechá-la e reabri-la quantas vezes for necessário, sem risco.
:::

## O que a aplicação modifica

Aplicar o changeset atualiza a tabela `CatalogEntry` (e `CatalogState` para memorizar a nova versão carregada). **Não provisiona** os novos datasets nem remove os datasets Climweb existentes — essa é a responsabilidade de **Synchronize with Climweb**:

```
1. Review changes   → atualiza o catálogo do plugin (CatalogEntry)
2. Synchronize      → propaga a seleção para o Climweb (Dataset)
```

Concretamente, depois de um *Apply*:

- as **new** aparecem como `pending_add` 🟠 na árvore,
- as **updated** continuam em `synced` 🟢 mas seu conteúdo de origem é atualizado — a próxima sincronia re-provisionará o `Dataset`,
- as **to remove** passam para `pending_remove` 🔴 — a próxima sincronia as removerá do Climweb,
- as **local drift** são deixadas como estão (você manterá assim suas edições manuais enquanto não clicar em `overwrite`).

## Quando clicar em Synchronize?

Logo após *Apply*. Sem sincronia, o Climweb continua servindo o conteúdo antigo para as camadas afetadas.
