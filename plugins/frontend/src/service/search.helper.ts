import type { EndpointLayer } from '@/service/mapServices.helper.ts'

/**
 * Look for a pattern in layer name or title, case insensitive
 * @param layers An array of layer definition
 * @param searchPattern The pattern to search
 * @returns The filtered array of layers
 */
export function searchPatternInLayers(layers: EndpointLayer[], searchPattern: string) {
  const s = searchPattern.toLowerCase()
  return searchPattern
    ? layers.filter((l) => l.name!.toLowerCase().includes(s) || l.title.toLowerCase().includes(s))
    : layers
}
