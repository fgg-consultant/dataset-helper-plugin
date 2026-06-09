# Limites administrativos

A aba **Admin Boundaries** inicializa a camada de limites administrativos do Climweb a partir dos **Common Operational Datasets da OCHA (COD-AB)** publicados no [HDX](https://data.humdata.org/). Este recurso é independente do catálogo de camadas WMS: ele alimenta o *boundary manager* do Climweb, que serve os limites como **tiles vetoriais (MVT)**.

## Pré-requisitos

- O **país** deve estar definido nas [configurações do plugin](./settings.md) (aba *Settings*). Os códigos ISO alfa-2 e alfa-3 são usados para localizar e filtrar os dados.
- A instância do Climweb deve incluir o *boundary manager* (`adminboundarymanager`) e o `geopandas`. Caso contrário, um aviso é exibido e o botão de importação fica desabilitado.

## Importar limites

Clique em **Import boundaries from OCHA**. O plugin executa todo o fluxo automaticamente:

1. **Localiza** o conjunto de dados COD-AB no HDX via API CKAN (`cod-ab-<iso3>`) e escolhe o arquivo shapefile (`*.shp.zip`).
2. **Baixa** o arquivo global (ele agrupa um shapefile por nível administrativo).
3. **Extrai** e detecta os níveis (`adm0`, `adm1`, …); camadas de linhas, pontos e capitais são ignoradas.
4. **Normaliza as colunas** de cada nível para o esquema esperado pelo boundary manager (`ADM{n}_EN`/`ADM{n}_FR` e `ADM{n}_PCODE`), reprojeta para EPSG:4326 e alinha `ADM0_PCODE` com o código do país.
5. **Recompacta por nível** e então **carrega** cada nível no boundary manager.

> O país é registrado primeiro nas configurações do boundary manager; caso contrário, seus sinais removeriam as linhas inseridas.

Ao finalizar, um painel resume quantas feições foram carregadas por nível:

```
Boundaries imported: 4 level(s), 416 features
```

## Níveis carregados

A tabela **Loaded admin levels** mostra quantas feições existem por nível para o país configurado:

| Nível | Conteúdo típico |
|-------|-----------------|
| 0 | País |
| 1 | Regiões |
| 2 | Províncias / departamentos |
| 3 | Municípios |
| 4 | (depende do país) |

## Pré-visualização do mapa

O mapa na parte inferior da aba mostra os limites servidos pelo boundary manager como tiles vetoriais:

```
/api/admin-boundary/tiles/{z}/{x}/{y}
```

Ele se centraliza automaticamente na caixa delimitadora do país. Após uma importação, o mapa é atualizado para mostrar os dados recém-carregados.

## Reimportar e limpar

- **Reimportar** é idempotente: para cada nível, os limites carregados anteriormente para este país são substituídos.
- **Clear boundaries** exclui todos os limites do país configurado (todos os níveis). Esta ação não pode ser desfeita.

## Fonte de dados

A fonte é **OCHA COD-AB** (Common Operational Datasets – Administrative Boundaries), os limites administrativos de referência usados pelas agências humanitárias, publicados no HDX.
