# Carregar um arquivo JSON

O botão **Load Config JSON** serve a dois usos distintos:

1. **Pré-visualizar o catálogo embarcado** entregue com o plugin (ação *Review embedded catalog*).
2. **Carregar um JSON personalizado** que você cola na área de texto.

Nos dois casos, o carregamento preenche ou atualiza a tabela `CatalogEntry`. **Nenhum objeto Climweb é criado enquanto você não clica em *Synchronize with Climweb***.

## Catálogo embarcado (caso padrão)

Veja a página dedicada [Atualizações do catálogo](./updates). O fluxo normal é:

1. **Review embedded catalog** → você vê o diff entre o JSON em disco e o catálogo na base.
2. **Apply changes** → a tabela `CatalogEntry` é atualizada, `CatalogState` memoriza a versão.
3. **Synchronize with Climweb** → os `Dataset` Climweb são criados / removidos / atualizados.

## JSON personalizado

Se você gerencia seu próprio arquivo de catálogo (além do catálogo embarcado ou no lugar dele), cole o conteúdo na área de texto e clique em **Load into Catalog**.

O plugin:

- cria as entradas ausentes,
- atualiza aquelas cujo conteúdo mudou,
- deixa as demais intactas.

As entradas criadas por essa via carregam a origem **`config`**, como as do catálogo embarcado. Consequência importante: se você carregar depois o catálogo embarcado, as entradas `config` que não aparecerem no JSON embarcado serão detectadas como **`to remove`** pela pré-visualização. Misturar várias fontes `config` exige, portanto, atenção.

## Formato esperado

O JSON deve seguir a estrutura aninhada **Categories → Subcategories → Datasets → Layers**:

```json
{
  "version": "2026.05.18",
  "schema_version": 1,
  "categories": [
    {
      "title": "Rainfall",
      "icon": "raindrops",
      "subcategories": [
        {
          "title": "Observation",
          "datasets": [
            {
              "title": "10-day precipitation estimate",
              "description": "...",
              "multi_temporal": true,
              "public": true,
              "metadata": {
                "function": "...",
                "resolution": "0.05deg",
                "source": "JRC eStation",
                "geographic_coverage": "Africa",
                "license": "Open Data",
                "frequency_of_update": "Dekadal",
                "overview": "...",
                "learn_more": "https://..."
              },
              "layers": [
                {
                  "type": "wms",
                  "title": "RFE 10-day",
                  "layer_name": "rfe_10d",
                  "wms_url": "https://example.org/wms",
                  "default": true,
                  "popup": true,
                  "legend_from_capabilities": true
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

Campos raiz:

| Campo              | Função                                                                        |
|--------------------|-------------------------------------------------------------------------------|
| `version`          | Identificador de versão do catálogo. Usado para detectar atualizações.        |
| `schema_version`   | Versão do esquema JSON. Incrementada quando a forma das entradas muda.        |
| `categories[]`     | Lista das categorias de mais alto nível.                                       |

Para as strings multilíngues, o catálogo embarcado usa um dicionário `{ "en": "...", "fr": "...", … }`. O plugin seleciona o idioma configurado em [Configurações](./settings) no carregamento. Uma string simples também é aceita.

## Tipos de camadas suportados

O campo `type` dentro de `layers[]` pode ser:

- `wms` — serviço WMS padrão (o mais comum).
- `raster_tile` / `vector_tile` — serviços de tiles XYZ ou PMTiles.
- `raster_file` / `vector_file` — arquivos baixáveis (com autenticação Bearer opcional).
- `raster_cog` — Cloud-Optimized GeoTIFF com template temporal.

Cada tipo tem seus próprios campos (URL template, intervalo temporal, estilo raster, configuração de popup…). Consulte o catálogo embarcado para exemplos completos.

### Campos específicos do WMS

Para as camadas `wms`, duas opções booleanas controlam o que é ativado no lado do Climweb:

| Campo                       | Padrão  | Efeito no `WmsLayer` do Climweb                                                                     |
|-----------------------------|---------|-----------------------------------------------------------------------------------------------------|
| `popup`                     | `false` | Ativa **Enable popup**: um popup é exibido ao clicar na camada.                                     |
| `legend_from_capabilities`  | `false` | Ativa **Load legend from WMS capabilities**: a legenda é lida do `<LegendURL>` do GetCapabilities.   |

Ambos são opt-in e devem ser definidos explicitamente por camada. A cada resync, o valor do JSON sobrescreve o valor do lado do Climweb.
