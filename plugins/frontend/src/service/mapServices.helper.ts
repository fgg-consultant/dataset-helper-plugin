import {
  WfsEndpoint,
  WmsEndpoint,
  type WmsLayerSummary,
  type WmtsLayer,
  type WfsFeatureTypeBrief,
  WmtsEndpoint,
} from '@camptocamp/ogc-client'

export type MTServiceProtocol = 'WFS' | 'WMS' | 'WMTS'
export type MTServiceVersion = '1.0.0' | '1.1.0' | '1.1.1' | '1.3.0' | '2.2.0'
export type EndpointLayer = WmsLayerSummary
export type MTServiceCapabilities = {
  title: string
  abstract: string
  layers?: EndpointLayer[]
}
