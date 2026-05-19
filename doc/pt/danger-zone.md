# Zona perigosa

A aba **Danger Zone** e o botão **Reset Catalog** da barra de ferramentas reúnem as ações **destrutivas**. Todas são irreversíveis; leia com atenção antes de clicar.

## Reset Catalog

Botão vermelho na barra do *Layer Catalog*. Essa ação:

1. **Remove todos os `Dataset` Climweb provisionados pelo plugin** (e somente esses: os datasets criados fora do plugin são preservados).
2. Remove os `Metadata` associados.
3. Varre as `SubCategory` e `Category` que ficaram vazias.
4. **Esvazia completamente a tabela `CatalogEntry`** (entradas `config`, `manual` e `wms_import` indistintamente).
5. Zera `CatalogState` — o plugin esquece qual versão do catálogo estava carregada.

Efeito líquido: o plugin volta ao estado do primeiro lançamento, e somente os dados Climweb criados fora do plugin sobrevivem.

**Quando usar:**

- Para começar do zero antes de carregar um catálogo diferente.
- Após uma má manipulação durante a fase de preparação.

**Quando não usar:**

- Em produção, em um Climweb que serve usuários. Prefira desativar seletivamente as camadas e sincronizar.

## Clear catalog-managed datasets

Botão na aba *Danger Zone*. Variante menos agressiva de *Reset Catalog*:

1. Remove os `Dataset` Climweb provisionados pelo plugin (idem acima).
2. Remove os `Metadata` associados.
3. Varre as taxonomias vazias.
4. **Conserva** a tabela `CatalogEntry`: as entradas voltam simplesmente para `pending_add` 🟠.

Efeito líquido: o Climweb é limpo do lado do plugin, mas sua seleção (quais camadas estão marcadas, seus acréscimos manuais…) permanece intacta. Clicar em **Synchronize with Climweb** em seguida recria tudo do zero com a seleção atual.

**Caso de uso típico:** resolver uma derivação persistente do conteúdo do lado do Climweb (títulos editados à mão, versões antigas de camadas que você quer sobrescrever de forma limpa).

## Clear All Datasets & Categories

Botão vermelho no fim da aba *Danger Zone*. **Nuclear**:

- Remove **todos** os `Dataset`, `SubCategory` e `Category` do geomanager do Climweb, sejam do plugin ou não.
- Remove todos os `WmsLayer`, `WmsRequestLayer`, `RasterStyle`, `Metadata`.
- Zera os `dataset_id` das `CatalogEntry`.

Efeito líquido: o mapviewer do Climweb fica sem nenhuma camada.

**Só utilize se entender exatamente o que está fazendo** — por exemplo durante uma reinicialização completa do ambiente.

## Tabela resumo

| Ação                                | `CatalogEntry` plugin | `Dataset` plugin | `Dataset` fora do plugin | `Category` / `SubCategory` |
|-------------------------------------|:---------------------:|:----------------:|:------------------------:|:--------------------------:|
| Desmarcar + Synchronize             | preservadas           | removidos        | preservados              | preservadas se não vazias  |
| Clear catalog-managed datasets      | preservadas (`pending_add`) | removidos | preservados              | sweep se vazias            |
| Reset Catalog                       | removidas             | removidos        | preservados              | sweep se vazias            |
| Clear All Datasets & Categories     | `dataset_id` zerado   | removidos        | **removidos**            | **removidas**              |
