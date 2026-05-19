# Configurações

O painel **Settings** fica no topo da aba *Layer Catalog*, recolhido sob os contadores. Reúne as configurações globais do plugin (um único conjunto de valores por instância Climweb).

Enquanto uma configuração obrigatória estiver ausente, um aviso *« required setting missing »* aparece no título do painel.

## Language

Idioma no qual as etiquetas do catálogo embarcado serão importadas (títulos, descrições, metadados). O catálogo embarcado é multilíngue; esta preferência apenas diz *qual* tradução será copiada para os `Dataset` e `Metadata` do Climweb no momento do carregamento.

Valores possíveis: `en`, `fr`, `es`, `pt`, `ar`.

Mudar o idioma **após** um carregamento não renomeia os datasets já criados; é preciso recarregar o catálogo (`Review embedded catalog` → `Apply`) para propagar as novas etiquetas.

## Country *(obrigatório)*

O país alvo da instância Climweb. Selecione-o na lista suspensa (preenchida ao abrir).

Este valor na verdade armazena quatro informações vinculadas:

- **alpha-3** (ex.: `bfa`) — substitui `{country_alpha3}` nas URLs das camadas.
- **alpha-2** (ex.: `bf`) — substitui `{country_alpha2}`.
- **nome oficial** (do OpenStreetMap Nominatim) — usado para exibição.
- **bounding box** `[south, north, west, east]` (do Nominatim) — enquadramento inicial das camadas no mapa.

Enquanto `Country` não estiver definido, o carregamento do catálogo embarcado recusará ou ignorará as camadas cuja URL contenha um marcador de país.

## ECMWF Token

Token para o serviço WMS `eccharts.ecmwf.int`. As camadas privadas do catálogo embarcado têm uma URL do tipo `…?token={ECMWF_TOKEN}`.

- **Vazio**: as camadas privadas são **ignoradas** no carregamento (contador `skipped_ecmwf_no_token`). As camadas públicas (`token=public`) passam normalmente.
- **Preenchido**: `{ECMWF_TOKEN}` é substituído onde o marcador aparecer.

## Local eStation URL

URL de uma instância eStation local, por exemplo `https://burkina.example.org/http/c000/w04/climsa/mobile-app`.

- **Vazia**: todas as camadas eStation do catálogo são importadas.
- **Preenchida**: o plugin consulta a instância e **só mantém** os produtos que ela realmente serve (contador `skipped_estation` para os demais).

Útil quando você implanta o Climweb apoiado em uma eStation local que só expõe parte dos produtos do catálogo JRC.

## Salvar

O botão **Save Settings** persiste os valores e exibe uma breve mensagem de confirmação. Sem efeito colateral no Climweb: as configurações só se propagam na próxima ação de carregamento ou sincronia.
