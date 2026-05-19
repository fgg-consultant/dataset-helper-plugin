# Sincronizar com o Climweb

O botão **Synchronize with Climweb** (barra de ferramentas do *Layer Catalog*) propaga o estado atual do catálogo para a base de dados do Climweb. É a única ação que realmente cria ou remove `Dataset` no geomanager.

## O que a sincronia faz

O plugin percorre todas as entradas e age conforme o status delas:

| Status              | Ação                                                                                          |
|---------------------|------------------------------------------------------------------------------------------------|
| `pending_add` 🟠     | Provisiona no Climweb: cria/reutiliza `Category` e `SubCategory`, cria `Dataset`, `Metadata`, depois os objetos de camada (`WmsLayer`, `WmsRequestLayer`, etc. conforme o tipo). |
| `pending_remove` 🔴  | Desprovisiona: remove o `Dataset` (e seus dependentes) do lado do Climweb, libera `dataset_id`. |
| `synced` 🟢          | Verifica que o `Dataset` ainda existe. Se o conteúdo do catálogo mudou desde a última sincronia, **re-provisiona** (título, URL ou metadados são atualizados). |
| `disabled` ⚪        | Nada a fazer.                                                                                  |

No final, um painel de resultados resume a passagem:

```
Sync complete: 12 added, 3 removed, 5 updated, 0 orphans cleared
```

## Casos particulares

### Órfãos

Se uma entrada estiver marcada como `synced` mas o `Dataset` Climweb foi removido entretanto (por exemplo via a administração do Wagtail), ela é detectada como **órfã**: `dataset_id` é zerado e a entrada volta para `pending_add`. Uma segunda sincronia a recriará.

O contador **orphans cleared** no painel de resultados reflete essas reconciliações.

### Categorias e subcategorias compartilhadas

O plugin **nunca remove** uma `Category` ou `SubCategory` que ainda contenha `Dataset` não gerenciados pelo plugin. Se você criou manualmente um dataset em uma categoria que o plugin também usa, desprovisionar as entradas do plugin não apagará essa categoria.

As categorias vazias, sim, são varridas ao final do ciclo (veja [Zona perigosa](./danger-zone)).

### Camadas do tipo `raster_file`

As camadas `raster_file` (arquivos raster baixados e armazenados no Climweb) **não são re-provisionadas** automaticamente quando o catálogo muda: sobrescrevê-las destruiria os arquivos já enviados. O plugin sinaliza esse caso pelo contador `raster_file drift` e deixa o objeto Climweb intacto. Para aplicar o novo conteúdo, remova a entrada e recrie-a (ou esvazie as camadas e ressincronize).

## O que fazer depois da sincronia

Após uma sincronia bem-sucedida, as camadas ficam visíveis no mapviewer do Climweb. Do lado do plugin:

- todas as entradas marcadas estão em `synced`,
- todas as desmarcadas estão em `disabled`.

Você pode retocar a seleção a qualquer momento e clicar novamente em **Synchronize with Climweb**: só a diferença desde a última sincronia será aplicada.
