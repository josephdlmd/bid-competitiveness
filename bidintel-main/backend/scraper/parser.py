"""HTML parser for extracting data from PhilGEPS pages.

Updated to match ACTUAL PhilGEPS HTML structure based on real pages.
"""

from bs4 import BeautifulSoup
from datetime import datetime, timezone
from typing import Dict, List, Optional
from utils.logger import logger
import re


class PhilGEPSParser:
    """Parses PhilGEPS HTML pages to extract structured data."""

    def __init__(self, html: str):
        """
        Initialize parser with HTML content.

        Args:
            html: HTML content to parse
        """
        self.soup = BeautifulSoup(html, 'lxml')

    def parse_bid_notice(self) -> Dict:
        """
        Parse a bid notice detail page.

        Returns all 35+ fields from BID_DATA_FIELDS.md
        Based on actual PhilGEPS structure from /tenders/viewBidNotice/{id}

        Returns:
            dict: Extracted bid notice data
        """
        try:
            logger.debug("Parsing bid notice (using BID_DATA_FIELDS.md)")

            data = {
                # CRITICAL FIELDS
                'reference_number': self._extract_reference_number(),  # Field #1
                'status': self._extract_status(),  # Field #2
                'control_number': self._extract_control_number(),  # Field #3
                'approved_budget': self._extract_budget(),  # Field #4
                'bid_form_fee': self._extract_bid_form_fee(),  # Field #6
                'title': self._extract_title(),  # Field #7
                'description': self._extract_description(),  # Field #8
                'classification': self._extract_classification(),  # Field #9
                'category': self._extract_category(),  # Field #10
                'procurement_mode': self._extract_procurement_mode(),  # Field #11
                'procurement_rules': self._extract_procurement_rules(),  # Field #12
                'lot_type': self._extract_lot_type(),  # Field #13

                # TIMELINE FIELDS
                'publish_date': self._extract_publish_date(),  # Field #14
                'closing_date': self._extract_closing_date(),  # Field #15
                'date_last_updated': self._extract_date_last_updated(),  # Field #16
                'bid_validity_days': self._extract_bid_validity_period(),  # Field #17
                'date_created': self._extract_date_created(),  # Field #18

                # DELIVERY FIELDS
                'delivery_period': self._extract_delivery_period(),  # Field #19
                'delivery_location': self._extract_delivery_location(),  # Field #20
                'agency_address': self._extract_agency_address(),  # Field #21

                # AGENCY FIELDS
                'procuring_entity': self._extract_procuring_entity(),  # Field #22
                'contact_person': self._extract_contact_person(),  # Field #23
                'contact_email': self._extract_contact_email(),  # Related to #23
                'contact_phone': self._extract_contact_phone(),  # Related to #23
                'created_by': self._extract_created_by(),  # Field #24
                'funding_source': self._extract_funding_source(),  # Field #25

                # LINE ITEMS (CRITICAL)
                'line_items': self._extract_line_items(),  # Field #26

                # SUPPLEMENTARY DATA
                'download_count': self._extract_download_count(),  # Field #35

                # META
                'scraped_at': datetime.now(timezone.utc)
            }

            logger.debug(f"Parsed bid notice: {data.get('reference_number')} (ALL FIELDS)")
            return data

        except Exception as e:
            logger.error(f"Error parsing bid notice: {str(e)}")
            raise

    def parse_bid_list_page(self) -> List[Dict]:
        """
        Parse a page containing list of bid notices.

        Based on actual PhilGEPS table structure from listing page.

        Returns:
            list: List of bid notice summaries with URLs
        """
        try:
            logger.debug("Parsing bid list page...")

            bids = []

            # Find all table rows - PhilGEPS uses td with data-label attributes
            rows = self.soup.select('tbody tr')

            for row in rows:
                try:
                    # Extract reference number and URL
                    ref_cell = row.find('td', {'data-label': 'Bid Notice Reference Number'})
                    if not ref_cell:
                        continue

                    ref_link = ref_cell.find('a')
                    if not ref_link:
                        continue

                    reference_number = ref_link.get_text(strip=True)
                    url = ref_link.get('href', '')

                    # Extract other fields using data-label
                    title_cell = row.find('td', {'data-label': 'Notice Title'})
                    title = title_cell.get_text(strip=True) if title_cell else None

                    class_cell = row.find('td', {'data-label': 'Classification'})
                    classification = class_cell.get_text(strip=True) if class_cell else None

                    agency_cell = row.find('td', {'data-label': 'Agency Name'})
                    procuring_entity = agency_cell.get_text(strip=True) if agency_cell else None

                    pub_date_cell = row.find('td', {'data-label': 'Publish Date'})
                    publish_date_str = pub_date_cell.get_text(strip=True) if pub_date_cell else None

                    # PhilGEPS uses "Due Date" for closing date in listing
                    closing_cell = row.find('td', {'data-label': 'Due Date'})
                    closing_date_str = closing_cell.get_text(strip=True) if closing_cell else None

                    status_cell = row.find('td', {'data-label': 'Status'})
                    status = status_cell.get_text(strip=True) if status_cell else None

                    bid = {
                        'reference_number': reference_number,
                        'title': title,
                        'classification': classification,
                        'procuring_entity': procuring_entity,
                        'publish_date': self._parse_date(publish_date_str),
                        'closing_date': self._parse_date(closing_date_str),
                        'status': status,
                        'url': url
                    }
                    bids.append(bid)

                except Exception as e:
                    logger.warning(f"Error parsing bid row: {str(e)}")
                    continue

            logger.info(f"Parsed {len(bids)} bid notices from list")
            return bids

        except Exception as e:
            logger.error(f"Error parsing bid list: {str(e)}")
            return []

    # Helper methods for extracting specific fields from detail page

    def _extract_reference_number(self) -> Optional[str]:
        """Extract bid reference number from detail page."""
        # Pattern: <label>Notice Reference Number :7297</label>
        label = self.soup.find('label', string=re.compile(r'Notice Reference Number'))
        if label:
            text = label.get_text(strip=True)
            # Extract number after colon
            match = re.search(r':(\d+)', text)
            if match:
                return match.group(1)
        return None

    def _extract_title(self) -> Optional[str]:
        """Extract bid title from detail page."""
        # PhilGEPS puts title in a bold center tag
        # Pattern: <b>Purchase of Meals...</b> inside a center tag with class verdhana_fourteenpx
        center = self.soup.find('center', class_='verdhana_fourteenpx')
        if center:
            bold_tag = center.find('b')
            if bold_tag:
                return bold_tag.get_text(strip=True)
        return None

    def _extract_procuring_entity(self) -> Optional[str]:
        """Extract procuring entity name from detail page."""
        # Try Method 1: <center class="verdhana_bold_twelvepx">DUTY FREE PHILIPPINES CORPORATION</center>
        center = self.soup.find('center', class_='verdhana_bold_twelvepx')
        if center:
            text = center.get_text(strip=True)
            if text:
                return text

        # Try Method 2: <label>Client Agency: </label><br>CITY GOVERNMENT OF BACOOR
        label = self.soup.find('label', string=re.compile(r'Client Agency:'))
        if label:
            # Get next sibling text after <br>
            next_text = self._get_text_after_label(label)
            if next_text:
                return next_text.strip()

        return None

    def _extract_classification(self) -> Optional[str]:
        """Extract classification (Goods/Services/Infrastructure) from detail page."""
        # Pattern: <label>Classification: </label><br>Goods<br><br>
        label = self.soup.find('label', string=re.compile(r'Classification:'))
        if label:
            return self._get_text_after_label(label)
        return None

    def _extract_category(self) -> Optional[str]:
        """Extract business category from detail page."""
        # Pattern: <label>Business Category: </label><br>Restaurants and catering
        label = self.soup.find('label', string=re.compile(r'Business Category:'))
        if label:
            return self._get_text_after_label(label)
        return None

    def _extract_budget(self) -> Optional[float]:
        """Extract approved budget from detail page."""
        # Pattern: <label>Approved Budget of the Contract: </label><br>70,000.00
        label = self.soup.find('label', string=re.compile(r'Approved Budget'))
        if label:
            budget_text = self._get_text_after_label(label)
            if budget_text:
                # Remove commas and convert to float
                numbers = re.sub(r'[^\d.]', '', budget_text)
                try:
                    return float(numbers)
                except ValueError:
                    return None
        return None

    def _extract_status(self) -> Optional[str]:
        """Extract bid status from detail page."""
        # Pattern: <label>Status :</label>&nbsp; [status text]
        label = self.soup.find('label', string=re.compile(r'Status\s*:'))
        if label:
            # Status might be in next text node or sibling
            status = self._get_text_after_label(label)
            if status:
                return status.strip()
        return "Published"  # Default status from listing page

    def _extract_publish_date(self) -> Optional[datetime]:
        """Extract publish date from detail page."""
        # Pattern: <label>Published Date: </label><br>13-Nov-2025 12:00 AM
        label = self.soup.find('label', string=re.compile(r'Published Date:'))
        if label:
            date_text = self._get_text_after_label(label)
            return self._parse_date(date_text)
        return None

    def _extract_closing_date(self) -> Optional[datetime]:
        """Extract closing date from detail page."""
        # Pattern: <label>Closing Date:</label><br>  20-Nov-2025 12:00 PM
        label = self.soup.find('label', string=re.compile(r'Closing Date:'))
        if label:
            date_text = self._get_text_after_label(label)
            return self._parse_date(date_text)
        return None

    def _extract_description(self) -> Optional[str]:
        """Extract description from detail page."""
        # Description is in the "Description:" row in the project details table
        # Look for <b>Description:</b> in a table cell
        desc_cell = None
        for td in self.soup.find_all('td'):
            if 'Description:' in td.get_text():
                desc_cell = td
                break

        if desc_cell:
            # Get the content, might be in nested div
            desc_div = desc_cell.find('div', class_='wrapped-long-string1')
            if desc_div:
                # Clean up the text, removing excessive whitespace
                text = desc_div.get_text(separator=' ', strip=True)
                return ' '.join(text.split())
        return None

    def _extract_contact_person(self) -> Optional[str]:
        """Extract contact person from detail page."""
        # Pattern: <label>Contact Person: </label><br>Fatima San Diego
        label = self.soup.find('label', string=re.compile(r'Contact Person:'))
        if label:
            return self._get_text_after_label(label)
        return None

    def _extract_contact_email(self) -> Optional[str]:
        """Extract contact email from detail page."""
        # Look for email patterns in the page
        # PhilGEPS may not always have explicit email labels
        text = self.soup.get_text()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None

    def _extract_contact_phone(self) -> Optional[str]:
        """Extract contact phone from detail page."""
        # Look for phone patterns
        # PhilGEPS structure varies, might not have explicit phone
        return None

    def _extract_delivery_period(self) -> Optional[str]:
        """Extract delivery period from detail page."""
        # Pattern: <label>Delivery Period: </label><br>30 Day(s)
        label = self.soup.find('label', string=re.compile(r'Delivery Period:'))
        if label:
            return self._get_text_after_label(label)
        return None

    # NEWLY ADDED EXTRACTION METHODS (from BID_DATA_FIELDS.md)

    def _extract_control_number(self) -> Optional[str]:
        """
        Extract control number (Field #3, line 577).

        Reference: BID_DATA_FIELDS.md Field #3
        Pattern: <label>Control Number: </label><br>25011520108<br>
        """
        label = self.soup.find('label', string=re.compile(r'Control Number:', re.IGNORECASE))
        if label:
            return self._get_text_after_label(label)
        return None

    def _extract_bid_form_fee(self) -> Optional[float]:
        """
        Extract bid form fee (Field #6, line 698-699).

        Reference: BID_DATA_FIELDS.md Field #6
        """
        label = self.soup.find('label', string=re.compile(r'Bid.*Form.*Fee:', re.IGNORECASE))
        if label:
            fee_text = self._get_text_after_label(label)
            if fee_text:
                numbers = re.sub(r'[^\d.]', '', fee_text)
                try:
                    return float(numbers) if numbers else 0.0
                except ValueError:
                    return 0.0
        return 0.0

    def _extract_procurement_mode(self) -> Optional[str]:
        """
        Extract procurement mode (Field #11, line 582).

        Reference: BID_DATA_FIELDS.md Field #11
        Example: "Public Bidding", "Limited Source Bidding"
        """
        label = self.soup.find('label', string=re.compile(r'Procurement Mode:', re.IGNORECASE))
        if label:
            return self._get_text_after_label(label)
        return None

    def _extract_procurement_rules(self) -> Optional[str]:
        """
        Extract applicable procurement rules (Field #12, line 584).

        Reference: BID_DATA_FIELDS.md Field #12
        Example: "Implementing Rules and Regulations"
        """
        label = self.soup.find('label', string=re.compile(r'Applicable.*Procurement.*Rules', re.IGNORECASE))
        if label:
            return self._get_text_after_label(label)
        return None

    def _extract_lot_type(self) -> Optional[str]:
        """
        Extract lot type (Field #13, line 578).

        Reference: BID_DATA_FIELDS.md Field #13
        Example: "Single Lot", "Multiple Lots"
        """
        label = self.soup.find('label', string=re.compile(r'Lot Type:', re.IGNORECASE))
        if label:
            return self._get_text_after_label(label)
        return None

    def _extract_date_last_updated(self) -> Optional[datetime]:
        """
        Extract last updated date (Field #16, line 695).

        Reference: BID_DATA_FIELDS.md Field #16
        """
        label = self.soup.find('label', string=re.compile(r'Date Last Updated:', re.IGNORECASE))
        if label:
            date_text = self._get_text_after_label(label)
            return self._parse_date(date_text)
        return None

    def _extract_bid_validity_period(self) -> Optional[int]:
        """
        Extract bid validity period in days (Field #17, line 575-576).

        Reference: BID_DATA_FIELDS.md Field #17
        Example: "120 Day(s)" -> 120
        """
        label = self.soup.find('label', string=re.compile(r'Bid.*Validity.*Period:', re.IGNORECASE))
        if label:
            text = self._get_text_after_label(label)
            if text:
                # Extract number from text like "120 Day(s)"
                match = re.search(r'(\d+)', text)
                if match:
                    try:
                        return int(match.group(1))
                    except ValueError:
                        return None
        return None

    def _extract_date_created(self) -> Optional[datetime]:
        """
        Extract date created (Field #18, line 592).

        Reference: BID_DATA_FIELDS.md Field #18
        """
        label = self.soup.find('label', string=re.compile(r'Date Created:', re.IGNORECASE))
        if label:
            date_text = self._get_text_after_label(label)
            return self._parse_date(date_text)
        return None

    def _extract_delivery_location(self) -> Optional[str]:
        """
        Extract delivery/project location (Field #20, line 586).

        Reference: BID_DATA_FIELDS.md Field #20
        Example: "Cavite"
        NOTE: This is DIFFERENT from delivery_period!
        """
        label = self.soup.find('label', string=re.compile(r'Delivery.*Location:|Project.*Location:', re.IGNORECASE))
        if label:
            return self._get_text_after_label(label)
        return None

    def _extract_agency_address(self) -> Optional[str]:
        """
        Extract full agency address (Field #21, lines 601-604).

        Reference: BID_DATA_FIELDS.md Field #21
        Example: "Bacoor Government Center Bayanan, Bacoor, Cavite, Region IV-A"
        """
        # Try Method 1: <center class="verdhana_twelvepx">Columbia Complex, Ninoy Aquino Avenue...</center>
        center = self.soup.find('center', class_='verdhana_twelvepx')
        if center:
            text = center.get_text(strip=True)
            if text:
                return text

        # Try Method 2: <label>Address: </label><br>...
        label = self.soup.find('label', string=re.compile(r'Address:', re.IGNORECASE))
        if label:
            # May need to concatenate multiple text nodes for full address
            address_parts = []
            for sibling in label.next_siblings:
                if sibling.name == 'br':
                    continue
                if isinstance(sibling, str):
                    text = sibling.strip()
                    if text and text not in ['', '\n']:
                        address_parts.append(text)
                elif sibling.name:
                    break
            return ' '.join(address_parts) if address_parts else None

        return None

    def _extract_created_by(self) -> Optional[str]:
        """
        Extract created by (Field #24, line 591).

        Reference: BID_DATA_FIELDS.md Field #24
        """
        label = self.soup.find('label', string=re.compile(r'Created By:', re.IGNORECASE))
        if label:
            return self._get_text_after_label(label)
        return None

    def _extract_funding_source(self) -> Optional[str]:
        """
        Extract funding source (Field #25, line 585).

        Reference: BID_DATA_FIELDS.md Field #25
        Example: "Regular Agency Fund (01000000)"
        """
        label = self.soup.find('label', string=re.compile(r'Funding Source:', re.IGNORECASE))
        if label:
            return self._get_text_after_label(label)
        return None

    def _extract_line_items(self) -> List[Dict]:
        """
        Extract line items table (Field #26, lines 664-683).

        Reference: BID_DATA_FIELDS.md Field #26 - MOST CRITICAL
        Returns: List of line item dictionaries

        Structure:
        - Item No.
        - UNSPSC (Universal Product/Service Code)
        - Lot Name
        - Lot Description
        - Quantity
        - Unit of Measure
        """
        line_items = []

        try:
            # Find the line items table
            # Look for text "Line Item Details" followed by table
            line_item_header = self.soup.find(string=re.compile(r'Line Item Details', re.IGNORECASE))

            if line_item_header:
                # Find the next table after this header
                table = line_item_header.find_next('table')

                if table:
                    # Find all rows except header
                    rows = table.find_all('tr')[1:]  # Skip header row

                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 6:
                            # Extract quantity as float
                            quantity_text = cols[4].get_text(strip=True)
                            quantity = None
                            if quantity_text:
                                try:
                                    quantity = float(re.sub(r'[^\d.]', '', quantity_text))
                                except ValueError:
                                    quantity = None

                            line_item = {
                                'item_number': int(cols[0].get_text(strip=True)) if cols[0].get_text(strip=True).isdigit() else None,
                                'unspsc_code': cols[1].get_text(strip=True),
                                'lot_name': cols[2].get_text(strip=True),
                                'lot_description': cols[3].get_text(strip=True),
                                'quantity': quantity,
                                'unit_of_measure': cols[5].get_text(strip=True),
                            }
                            line_items.append(line_item)

            logger.debug(f"Extracted {len(line_items)} line items")
            return line_items

        except Exception as e:
            logger.error(f"Error extracting line items: {e}")
            return []

    def _extract_download_count(self) -> int:
        """
        Extract number of downloads (Field #35, line 706-707).

        Reference: BID_DATA_FIELDS.md Field #35
        """
        try:
            # Look for download count pattern
            text = self.soup.get_text()
            match = re.search(r'Downloaded:\s*(\d+)', text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        except Exception as e:
            logger.debug(f"Could not extract download count: {e}")
        return 0

    # Utility methods

    def _get_text_after_label(self, label) -> Optional[str]:
        """
        Get text content after a label tag.

        PhilGEPS pattern: <label>Field: </label><br>VALUE<br><br>

        Args:
            label: BeautifulSoup label tag

        Returns:
            str: Text content after the label, or None
        """
        if not label:
            return None

        # Navigate through siblings to find text
        for sibling in label.next_siblings:
            if sibling.name == 'br':
                continue
            if isinstance(sibling, str):
                text = sibling.strip()
                if text:
                    return text
            elif sibling.name:
                # If we hit another tag, get its text
                text = sibling.get_text(strip=True)
                if text:
                    return text
        return None

    @staticmethod
    def _parse_date(date_string: Optional[str]) -> Optional[datetime]:
        """
        Parse date string to datetime object.

        PhilGEPS uses formats like:
        - "13-Nov-2025 12:00 AM"
        - "02-Dec-2025 08:30 AM"
        - "13-Nov-2025"

        Args:
            date_string: Date string to parse

        Returns:
            datetime: Parsed datetime or None
        """
        if not date_string:
            return None

        date_string = date_string.strip()

        # PhilGEPS date formats
        formats = [
            '%d-%b-%Y %I:%M %p',  # 13-Nov-2025 12:00 AM
            '%d-%b-%Y',            # 13-Nov-2025
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%m/%d/%Y',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue

        logger.warning(f"Could not parse date: {date_string}")
        return None

    def parse_document_links(self) -> List[Dict]:
        """
        Parse PDF document links from the preview/tender_doc_view page.

        Returns:
            list: List of document dictionaries with filename and URL
        """
        try:
            documents = []

            # Strategy 1: Find all PDF links by href ending with .pdf
            # Pattern: <a target="_blank" href="https://philgeps.gov.ph/portal_documents/bid_notice_documents/bid_notice_7244/bid_notice_document/1762836649_25750220105pr.pdf">
            pdf_links = self.soup.find_all('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
            logger.debug(f"Strategy 1: Found {len(pdf_links)} PDF links by href pattern")

            # Strategy 2: Also find links containing 'portal_documents' in href (backup)
            if len(pdf_links) == 0:
                portal_doc_links = self.soup.find_all('a', href=re.compile(r'portal_documents.*\.pdf', re.IGNORECASE))
                logger.debug(f"Strategy 2: Found {len(portal_doc_links)} PDF links by portal_documents pattern")
                pdf_links.extend(portal_doc_links)

            # Strategy 3: Find any links with .pdf extension in the URL
            if len(pdf_links) == 0:
                all_links = self.soup.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href', '')
                    if '.pdf' in href.lower():
                        pdf_links.append(link)
                logger.debug(f"Strategy 3: Found {len(pdf_links)} total PDF links")

            # Log a sample of the HTML if no documents found for debugging
            if len(pdf_links) == 0:
                # Get a sample of links on the page for debugging
                all_links = self.soup.find_all('a', href=True)
                logger.warning(f"No PDF links found. Total links on page: {len(all_links)}")
                if all_links:
                    sample_links = [str(link)[:100] for link in all_links[:5]]
                    logger.debug(f"Sample links: {sample_links}")

            for link in pdf_links:
                href = link.get('href', '').strip()
                if not href:
                    continue

                # Extract filename from URL or link text
                filename = link.get_text(strip=True) or href.split('/')[-1]

                # Handle relative URLs
                if href.startswith('/'):
                    href = f"https://philgeps.gov.ph{href}"
                elif not href.startswith('http'):
                    href = f"https://philgeps.gov.ph/{href}"

                document = {
                    'filename': filename,
                    'document_url': href,
                    'document_type': self._guess_document_type(filename)
                }

                documents.append(document)
                logger.debug(f"Added document: {filename} -> {href}")

            logger.debug(f"Successfully parsed {len(documents)} PDF documents")
            return documents

        except Exception as e:
            logger.error(f"Error parsing document links: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def _guess_document_type(self, filename: str) -> Optional[str]:
        """
        Guess document type from filename.

        Args:
            filename: Document filename

        Returns:
            str: Guessed document type or None
        """
        if not filename:
            return None

        filename_lower = filename.lower()

        # Common document type patterns
        if 'bid_notice' in filename_lower or 'notice' in filename_lower:
            return 'Bid Notice'
        elif 'technical' in filename_lower or 'specs' in filename_lower:
            return 'Technical Specifications'
        elif 'terms' in filename_lower or 'tor' in filename_lower:
            return 'Terms of Reference'
        elif 'bill' in filename_lower or 'boq' in filename_lower:
            return 'Bill of Quantities'
        elif 'drawing' in filename_lower or 'plan' in filename_lower:
            return 'Drawings/Plans'
        elif 'supplement' in filename_lower or 'amendment' in filename_lower:
            return 'Supplement/Amendment'
        else:
            return 'Document'

    # =========================================================================
    # AWARDED CONTRACTS PARSING METHODS
    # =========================================================================

    def parse_awarded_contract(self) -> Dict:
        """
        Parse an awarded contract detail page.

        Data Source:
        - Index: https://philgeps.gov.ph/Indexes/viewMoreAward
        - Detail: /Indexes/viewAwardNotice/{award_id}/MORE

        Returns all fields for AwardedContract model including:
        - Award Notice Number (primary ID)
        - Bid Reference Number (link to original bid)
        - Awardee information (winner)
        - ABC and Contract Amount (awarded price)
        - Contract details and dates

        Returns:
            dict: Extracted awarded contract data
        """
        try:
            logger.debug("Parsing awarded contract detail page")

            data = {
                # PRIMARY IDENTIFIERS
                'award_notice_number': self._extract_award_notice_number(),
                'bid_reference_number': self._extract_bid_reference_number(),
                'control_number': self._extract_control_number(),

                # AWARD INFORMATION
                'award_title': self._extract_title(),  # Reuse existing method
                'award_type': self._extract_award_type(),
                'award_date': self._extract_award_date(),

                # AWARDEE (WINNER) INFORMATION
                'awardee_name': self._extract_awardee_name(),
                'awardee_address': self._extract_awardee_address(),
                'awardee_contact_person': self._extract_awardee_contact_person(),
                'awardee_corporate_title': self._extract_awardee_corporate_title(),

                # FINANCIAL INFORMATION (CRITICAL)
                'approved_budget': self._extract_budget(),  # Reuse existing (ABC)
                'contract_amount': self._extract_contract_amount(),  # NEW - Awarded price

                # CONTRACT DETAILS
                'contract_number': self._extract_contract_number(),
                'contract_effectivity_date': self._extract_contract_effectivity_date(),
                'contract_end_date': self._extract_contract_end_date(),
                'period_of_contract': self._extract_period_of_contract(),
                'proceed_date': self._extract_proceed_date(),

                # PROCUREMENT DETAILS (reuse existing methods)
                'procurement_mode': self._extract_procurement_mode(),
                'classification': self._extract_classification(),
                'category': self._extract_category(),
                'procurement_rules': self._extract_procurement_rules(),
                'funding_source': self._extract_funding_source(),

                # PROCURING ENTITY
                'procuring_entity': self._extract_procuring_entity(),
                'agency_address': self._extract_agency_address(),
                'delivery_location': self._extract_delivery_location(),

                # TIMELINE
                'publish_date': self._extract_publish_date(),
                'date_created': self._extract_date_created(),
                'date_last_updated': self._extract_date_last_updated(),

                # DESCRIPTION
                'description': self._extract_description(),

                # ADDITIONAL
                'created_by': self._extract_created_by(),

                # LINE ITEMS (reuse existing)
                'line_items': self._extract_line_items(),

                # DOCUMENTS (View Document links)
                'documents': self._extract_award_documents(),

                # META
                'scraped_at': datetime.now(timezone.utc)
            }

            logger.debug(f"Parsed awarded contract: {data.get('award_notice_number')}")
            return data

        except Exception as e:
            logger.error(f"Error parsing awarded contract: {str(e)}")
            raise

    def _extract_award_notice_number(self) -> Optional[str]:
        """
        Extract Award Notice Number (primary identifier).

        HTML Example:
        <label>Award Notice Number :1998 </label>

        Returns:
            str: Award notice number (e.g., "1998")
        """
        try:
            # Method 1: Look for "Award Notice Number" label
            label = self.soup.find('label', string=re.compile(r'Award Notice Number', re.I))
            if label:
                text = label.get_text(strip=True)
                match = re.search(r'(\d+)', text)
                if match:
                    return match.group(1).strip()

            return None

        except Exception as e:
            logger.debug(f"Error extracting award notice number: {e}")
            return None

    def _extract_bid_reference_number(self) -> Optional[str]:
        """
        Extract Bid Notice Reference Number (links to original bid).

        HTML Example:
        <label>Notice Reference Number:</label><br>6793 <br><br>

        Returns:
            str: Bid reference number (e.g., "6793")
        """
        try:
            # Look for "Notice Reference Number" label
            label = self.soup.find('label', string=re.compile(r'Notice Reference Number', re.I))
            if label and label.next_sibling:
                # Get text after <br> tag
                sibling = label.find_next_sibling(string=True)
                if sibling:
                    ref_num = sibling.strip()
                    if ref_num:
                        return ref_num

            return None

        except Exception as e:
            logger.debug(f"Error extracting bid reference number: {e}")
            return None

    def _extract_award_type(self) -> Optional[str]:
        """
        Extract Award Type.

        HTML Example:
        <label>Award Type:</label><br>Award Notice<br><br>

        Returns:
            str: Award type (e.g., "Award Notice")
        """
        try:
            label = self.soup.find('label', string=re.compile(r'Award Type', re.I))
            if label:
                sibling = label.find_next_sibling(string=True)
                if sibling:
                    return sibling.strip()

            return None

        except Exception as e:
            logger.debug(f"Error extracting award type: {e}")
            return None

    def _extract_award_date(self) -> Optional[datetime]:
        """
        Extract Award Date.

        HTML Example:
        <label>Award Date:</label><br>12-Nov-2025<br><br>

        Returns:
            datetime: Award date
        """
        try:
            label = self.soup.find('label', string=re.compile(r'Award Date', re.I))
            if label:
                sibling = label.find_next_sibling(string=True)
                if sibling:
                    date_str = sibling.strip()
                    return self._parse_date(date_str)

            return None

        except Exception as e:
            logger.debug(f"Error extracting award date: {e}")
            return None

    def _extract_awardee_name(self) -> Optional[str]:
        """
        Extract Awardee Name (winner of the contract).

        HTML Example:
        <label class="tamoha_bold_twelvepx">Awardee:</label><br>
        <label class="tamoha_twelvepx"> LOUISE AND AEDAN ENTERPRISE INC.</label>

        Returns:
            str: Awardee company name
        """
        try:
            # Look for "Awardee:" label
            label = self.soup.find('label', string=re.compile(r'Awardee\s*:', re.I))
            if label:
                # Try to find next label with class tamoha_twelvepx
                next_label = label.find_next('label', class_='tamoha_twelvepx')
                if next_label:
                    return next_label.get_text(strip=True)

                # Fallback: get text after <br>
                sibling = label.find_next_sibling(string=True)
                if sibling:
                    awardee = sibling.strip()
                    if awardee:
                        return awardee

            return None

        except Exception as e:
            logger.debug(f"Error extracting awardee name: {e}")
            return None

    def _extract_awardee_address(self) -> Optional[str]:
        """
        Extract Awardee Address.

        HTML Example:
        <label>Address:</label><br>
        No. 19 Don Pedro Subdivision Talaibon, Ibaan, Batangas, Region IV-A, Philippines<br><br>

        Returns:
            str: Awardee address
        """
        try:
            # Find "Address:" label within awardee section
            labels = self.soup.find_all('label', string=re.compile(r'Address\s*:', re.I))

            # There might be multiple "Address" labels, we want the one near "Awardee"
            for label in labels:
                # Check if this is in the awardee section by looking for nearby "Awardee" text
                parent_text = label.parent.get_text() if label.parent else ''
                if 'Awardee' in parent_text or 'Corporate Title' in parent_text:
                    sibling = label.find_next_sibling(string=True)
                    if sibling:
                        address = sibling.strip()
                        if address and len(address) > 5:  # Avoid empty or very short strings
                            return address

            return None

        except Exception as e:
            logger.debug(f"Error extracting awardee address: {e}")
            return None

    def _extract_awardee_contact_person(self) -> Optional[str]:
        """
        Extract Awardee Contact Person.

        HTML Example:
        <label>Awardee Contact Person:</label><br>
        AXELL JAY  CATAPANG<br> <br>

        Returns:
            str: Contact person name
        """
        try:
            label = self.soup.find('label', string=re.compile(r'Awardee Contact Person', re.I))
            if label:
                sibling = label.find_next_sibling(string=True)
                if sibling:
                    contact = sibling.strip()
                    if contact:
                        return contact

            return None

        except Exception as e:
            logger.debug(f"Error extracting awardee contact person: {e}")
            return None

    def _extract_awardee_corporate_title(self) -> Optional[str]:
        """
        Extract Awardee Corporate Title.

        HTML Example:
        <label>Corporate Title:</label><br>
        Proprietor<br> <br>

        Returns:
            str: Corporate title
        """
        try:
            label = self.soup.find('label', string=re.compile(r'Corporate Title', re.I))
            if label:
                sibling = label.find_next_sibling(string=True)
                if sibling:
                    title = sibling.strip()
                    if title:
                        return title

            return None

        except Exception as e:
            logger.debug(f"Error extracting corporate title: {e}")
            return None

    def _extract_contract_amount(self) -> Optional[float]:
        """
        Extract Contract Amount (AWARDED PRICE - the actual winning bid amount).

        This is different from ABC (Approved Budget).
        This is the actual price the contract was awarded for.

        HTML Example:
        <label>Contract Amount:</label><br>PHP 750,000.00<br><br>

        Returns:
            float: Contract amount in PHP
        """
        try:
            label = self.soup.find('label', string=re.compile(r'Contract Amount', re.I))
            if label:
                sibling = label.find_next_sibling(string=True)
                if sibling:
                    amount_str = sibling.strip()
                    # Remove "PHP", commas, and convert to float
                    amount_str = re.sub(r'[^\d.]', '', amount_str)
                    if amount_str:
                        return float(amount_str)

            return None

        except Exception as e:
            logger.debug(f"Error extracting contract amount: {e}")
            return None

    def _extract_contract_number(self) -> Optional[str]:
        """
        Extract Contract Number.

        HTML Example:
        <label>Contract No.:</label><br><br><br>
        (might be empty)

        Returns:
            str: Contract number or None
        """
        try:
            label = self.soup.find('label', string=re.compile(r'Contract No', re.I))
            if label:
                sibling = label.find_next_sibling(string=True)
                if sibling:
                    contract_no = sibling.strip()
                    if contract_no and contract_no != '':
                        return contract_no

            return None

        except Exception as e:
            logger.debug(f"Error extracting contract number: {e}")
            return None

    def _extract_contract_effectivity_date(self) -> Optional[datetime]:
        """
        Extract Contract Effectivity Date.

        HTML Example:
        <label>Contract Effectivity Date:</label><br><br><br>
        (might be empty)

        Returns:
            datetime: Contract start date or None
        """
        try:
            label = self.soup.find('label', string=re.compile(r'Contract Effectivity Date', re.I))
            if label:
                sibling = label.find_next_sibling(string=True)
                if sibling:
                    date_str = sibling.strip()
                    if date_str:
                        return self._parse_date(date_str)

            return None

        except Exception as e:
            logger.debug(f"Error extracting contract effectivity date: {e}")
            return None

    def _extract_contract_end_date(self) -> Optional[datetime]:
        """
        Extract Contract End Date.

        HTML Example:
        <label>Contract End Date:</label><br><br><br>
        (might be empty)

        Returns:
            datetime: Contract end date or None
        """
        try:
            label = self.soup.find('label', string=re.compile(r'Contract End Date', re.I))
            if label:
                sibling = label.find_next_sibling(string=True)
                if sibling:
                    date_str = sibling.strip()
                    if date_str:
                        return self._parse_date(date_str)

            return None

        except Exception as e:
            logger.debug(f"Error extracting contract end date: {e}")
            return None

    def _extract_period_of_contract(self) -> Optional[str]:
        """
        Extract Period of Contract.

        HTML Example:
        <label>Period of Contract :</label><br>
        30-Day(s)<br><br>

        Returns:
            str: Period description (e.g., "30-Day(s)")
        """
        try:
            label = self.soup.find('label', string=re.compile(r'Period of Contract', re.I))
            if label:
                sibling = label.find_next_sibling(string=True)
                if sibling:
                    period = sibling.strip()
                    if period:
                        return period

            return None

        except Exception as e:
            logger.debug(f"Error extracting period of contract: {e}")
            return None

    def _extract_award_documents(self) -> List[Dict]:
        """
        Extract document links from awarded contract page.

        Looks for "View Document" links and other document downloads.

        HTML Example:
        <b>View Document</b> with href to document URL

        Returns:
            List[Dict]: List of document dictionaries with filename, url, type
        """
        documents = []

        try:
            # Method 1: Look for <b>View Document</b> links
            view_doc_tags = self.soup.find_all('b', string=re.compile(r'View Document', re.I))
            for tag in view_doc_tags:
                # Find parent <a> tag
                link = tag.find_parent('a')
                if link:
                    href = link.get('href', '').strip()
                    if href:
                        # Handle relative URLs
                        if href.startswith('/'):
                            href = f"https://philgeps.gov.ph{href}"
                        elif not href.startswith('http'):
                            href = f"https://philgeps.gov.ph/{href}"

                        documents.append({
                            'filename': 'Award Document',
                            'document_url': href,
                            'document_type': 'Award Document'
                        })

            # Method 2: Look for PDF links (alternative pattern)
            pdf_links = self.soup.find_all('a', href=re.compile(r'\.pdf|document|download', re.I))
            for link in pdf_links:
                href = link.get('href', '').strip()
                if not href or any(d['document_url'] == href for d in documents):
                    continue

                # Handle relative URLs
                if href.startswith('/'):
                    href = f"https://philgeps.gov.ph{href}"
                elif not href.startswith('http'):
                    href = f"https://philgeps.gov.ph/{href}"

                filename = link.get_text(strip=True) or href.split('/')[-1]

                documents.append({
                    'filename': filename,
                    'document_url': href,
                    'document_type': self._guess_document_type(filename)
                })

            logger.debug(f"Extracted {len(documents)} award documents")
            return documents

        except Exception as e:
            logger.error(f"Error extracting award documents: {str(e)}")
            return []

    def _extract_proceed_date(self) -> Optional[datetime]:
        """
        Extract Proceed Date.

        HTML Example:
        <label>Proceed Date:</label><br><br><br>
        (might be empty)

        Returns:
            datetime: Proceed date or None
        """
        try:
            label = self.soup.find('label', string=re.compile(r'Proceed Date', re.I))
            if label:
                sibling = label.find_next_sibling(string=True)
                if sibling:
                    date_str = sibling.strip()
                    if date_str:
                        return self._parse_date(date_str)

            return None

        except Exception as e:
            logger.debug(f"Error extracting proceed date: {e}")
            return None
