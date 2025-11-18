/**
 * Philippine Administrative Region Mapping
 * Maps provinces, cities, and delivery locations to their administrative regions
 */

export interface RegionInfo {
  code: string;
  name: string;
  fullName: string;
}

export const REGIONS: Record<string, RegionInfo> = {
  NCR: { code: 'NCR', name: 'NCR', fullName: 'National Capital Region' },
  CAR: { code: 'CAR', name: 'CAR', fullName: 'Cordillera Administrative Region' },
  I: { code: 'I', name: 'Region I', fullName: 'Ilocos Region' },
  II: { code: 'II', name: 'Region II', fullName: 'Cagayan Valley' },
  III: { code: 'III', name: 'Region III', fullName: 'Central Luzon' },
  'IV-A': { code: 'IV-A', name: 'Region IV-A', fullName: 'CALABARZON' },
  'IV-B': { code: 'IV-B', name: 'Region IV-B', fullName: 'MIMAROPA' },
  V: { code: 'V', name: 'Region V', fullName: 'Bicol Region' },
  VI: { code: 'VI', name: 'Region VI', fullName: 'Western Visayas' },
  VII: { code: 'VII', name: 'Region VII', fullName: 'Central Visayas' },
  VIII: { code: 'VIII', name: 'Region VIII', fullName: 'Eastern Visayas' },
  IX: { code: 'IX', name: 'Region IX', fullName: 'Zamboanga Peninsula' },
  X: { code: 'X', name: 'Region X', fullName: 'Northern Mindanao' },
  XI: { code: 'XI', name: 'Region XI', fullName: 'Davao Region' },
  XII: { code: 'XII', name: 'Region XII', fullName: 'SOCCSKSARGEN' },
  XIII: { code: 'XIII', name: 'Region XIII', fullName: 'Caraga' },
  BARMM: { code: 'BARMM', name: 'BARMM', fullName: 'Bangsamoro Autonomous Region in Muslim Mindanao' },
};

// Province/City to Region mapping
const LOCATION_TO_REGION: Record<string, string> = {
  // NCR - National Capital Region
  'Metro Manila': 'NCR',
  'Manila': 'NCR',
  'Quezon City': 'NCR',
  'Makati': 'NCR',
  'Pasig': 'NCR',
  'Taguig': 'NCR',
  'Mandaluyong': 'NCR',
  'Pasay': 'NCR',
  'Parañaque': 'NCR',
  'Las Piñas': 'NCR',
  'Muntinlupa': 'NCR',
  'Caloocan': 'NCR',
  'Malabon': 'NCR',
  'Navotas': 'NCR',
  'Valenzuela': 'NCR',
  'Marikina': 'NCR',
  'San Juan': 'NCR',

  // CAR - Cordillera Administrative Region
  'Abra': 'CAR',
  'Apayao': 'CAR',
  'Benguet': 'CAR',
  'Ifugao': 'CAR',
  'Kalinga': 'CAR',
  'Mountain Province': 'CAR',
  'Baguio': 'CAR',

  // Region I - Ilocos Region
  'Ilocos Norte': 'I',
  'Ilocos Sur': 'I',
  'La Union': 'I',
  'Pangasinan': 'I',

  // Region II - Cagayan Valley
  'Batanes': 'II',
  'Cagayan': 'II',
  'Isabela': 'II',
  'Nueva Vizcaya': 'II',
  'Quirino': 'II',
  'Tuguegarao': 'II',

  // Region III - Central Luzon
  'Aurora': 'III',
  'Bataan': 'III',
  'Bulacan': 'III',
  'Nueva Ecija': 'III',
  'Pampanga': 'III',
  'Tarlac': 'III',
  'Zambales': 'III',

  // Region IV-A - CALABARZON
  'Batangas': 'IV-A',
  'Cavite': 'IV-A',
  'Laguna': 'IV-A',
  'Quezon': 'IV-A',
  'Rizal': 'IV-A',

  // Region IV-B - MIMAROPA
  'Marinduque': 'IV-B',
  'Occidental Mindoro': 'IV-B',
  'Oriental Mindoro': 'IV-B',
  'Palawan': 'IV-B',
  'Romblon': 'IV-B',
  'Puerto Princesa': 'IV-B',

  // Region V - Bicol Region
  'Albay': 'V',
  'Camarines Norte': 'V',
  'Camarines Sur': 'V',
  'Catanduanes': 'V',
  'Masbate': 'V',
  'Sorsogon': 'V',
  'Naga': 'V',
  'Legazpi': 'V',

  // Region VI - Western Visayas
  'Aklan': 'VI',
  'Antique': 'VI',
  'Capiz': 'VI',
  'Guimaras': 'VI',
  'Iloilo': 'VI',
  'Negros Occidental': 'VI',
  'Bacolod': 'VI',
  'Iloilo City': 'VI',

  // Region VII - Central Visayas
  'Bohol': 'VII',
  'Cebu': 'VII',
  'Negros Oriental': 'VII',
  'Siquijor': 'VII',
  'Cebu City': 'VII',
  'Mandaue': 'VII',
  'Lapu-Lapu': 'VII',
  'Dumaguete': 'VII',

  // Region VIII - Eastern Visayas
  'Biliran': 'VIII',
  'Eastern Samar': 'VIII',
  'Leyte': 'VIII',
  'Northern Samar': 'VIII',
  'Samar': 'VIII',
  'Southern Leyte': 'VIII',
  'Tacloban': 'VIII',
  'Ormoc': 'VIII',

  // Region IX - Zamboanga Peninsula
  'Zamboanga Del Norte': 'IX',
  'Zamboanga Del Sur': 'IX',
  'Zamboanga Sibugay': 'IX',
  'Zamboanga City': 'IX',

  // Region X - Northern Mindanao
  'Bukidnon': 'X',
  'Camiguin': 'X',
  'Lanao Del Norte': 'X',
  'Misamis Occidental': 'X',
  'Misamis Oriental': 'X',
  'Cagayan de Oro': 'X',
  'Iligan': 'X',

  // Region XI - Davao Region
  'Davao de Oro': 'XI',
  'Davao Del Norte': 'XI',
  'Davao Del Sur': 'XI',
  'Davao Occidental': 'XI',
  'Davao Oriental': 'XI',
  'Davao City': 'XI',
  'Davao': 'XI',

  // Region XII - SOCCSKSARGEN
  'Cotabato': 'XII',
  'North Cotabato': 'XII',
  'Sarangani': 'XII',
  'South Cotabato': 'XII',
  'Sultan Kudarat': 'XII',
  'General Santos': 'XII',
  'Koronadal': 'XII',

  // Region XIII - Caraga
  'Agusan Del Norte': 'XIII',
  'Agusan Del Sur': 'XIII',
  'Dinagat Island': 'XIII',
  'Surigao Del Norte': 'XIII',
  'Surigao Del Sur': 'XIII',
  'Butuan': 'XIII',

  // BARMM - Bangsamoro Autonomous Region
  'Basilan': 'BARMM',
  'Lanao Del Sur': 'BARMM',
  'Maguindanao': 'BARMM',
  'Sulu': 'BARMM',
  'Tawi-Tawi': 'BARMM',
};

/**
 * Get administrative region from delivery location
 * @param deliveryLocation - The delivery location string (province, city, or location)
 * @returns Region info object or null if not found
 */
export function getRegionFromLocation(deliveryLocation: string | null | undefined): RegionInfo | null {
  if (!deliveryLocation) return null;

  // Normalize the location string
  const normalized = deliveryLocation.trim();

  // Check for exact match first
  const regionCode = LOCATION_TO_REGION[normalized];
  if (regionCode) {
    return REGIONS[regionCode];
  }

  // Check for partial match (case-insensitive)
  const lowerLocation = normalized.toLowerCase();
  for (const [location, code] of Object.entries(LOCATION_TO_REGION)) {
    if (lowerLocation.includes(location.toLowerCase()) || location.toLowerCase().includes(lowerLocation)) {
      return REGIONS[code];
    }
  }

  // Check if it's "Nationwide" or similar
  if (lowerLocation.includes('nationwide') || lowerLocation.includes('national')) {
    return { code: 'NATIONWIDE', name: 'Nationwide', fullName: 'Nationwide' };
  }

  return null;
}

/**
 * Get region display name (short format)
 * @param deliveryLocation - The delivery location string
 * @returns Region name (e.g., "Region IV-A") or "Unknown"
 */
export function getRegionName(deliveryLocation: string | null | undefined): string {
  const region = getRegionFromLocation(deliveryLocation);
  return region ? region.name : 'Unknown';
}

/**
 * Get region full display (e.g., "Region IV-A (CALABARZON)")
 * @param deliveryLocation - The delivery location string
 * @returns Full region display or "Unknown"
 */
export function getRegionFullDisplay(deliveryLocation: string | null | undefined): string {
  const region = getRegionFromLocation(deliveryLocation);
  if (!region) return 'Unknown';
  if (region.code === 'NCR' || region.code === 'CAR' || region.code === 'BARMM') {
    return `${region.code} (${region.fullName})`;
  }
  return `${region.name} (${region.fullName})`;
}

/**
 * Get all regions as options for dropdowns
 * @returns Array of region options sorted by code
 */
export function getAllRegions(): RegionInfo[] {
  return Object.values(REGIONS);
}

/**
 * Get region code from delivery location
 * @param deliveryLocation - The delivery location string
 * @returns Region code (e.g., "IV-A") or null
 */
export function getRegionCode(deliveryLocation: string | null | undefined): string | null {
  const region = getRegionFromLocation(deliveryLocation);
  return region ? region.code : null;
}
