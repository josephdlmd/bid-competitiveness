/**
 * Bid data enhancement utilities
 * Adds computed fields to bid data including administrative regions
 */

import { Bid } from '@/lib/types';
import { getRegionFromLocation, getRegionCode } from './regionMapping';

/**
 * Enhance a single bid with computed fields including administrative region
 * @param bid - The bid object to enhance
 * @returns Enhanced bid with administrative_region and region_code fields
 */
export function enhanceBid(bid: Bid): Bid {
  const region = getRegionFromLocation(bid.delivery_location);
  const regionCode = getRegionCode(bid.delivery_location);

  return {
    ...bid,
    administrative_region: region ? region.name : null,
    region_code: regionCode,
  };
}

/**
 * Enhance an array of bids with computed fields
 * @param bids - Array of bid objects to enhance
 * @returns Array of enhanced bids
 */
export function enhanceBids(bids: Bid[]): Bid[] {
  return bids.map(enhanceBid);
}
