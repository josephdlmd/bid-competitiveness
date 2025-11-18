"""SQLAlchemy database schemas/models - ALIGNED WITH BID_DATA_FIELDS.md"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class BidNotice(Base):
    """
    Bid Notice model - implements ALL 35+ fields from BID_DATA_FIELDS.md

    Reference: BID_DATA_FIELDS.md for complete field documentation
    """

    __tablename__ = 'bid_notices'

    # Meta fields
    id = Column(Integer, primary_key=True, autoincrement=True)

    # CRITICAL FIELDS (🔴 Priority from BID_DATA_FIELDS.md)

    # Field #1: Notice Reference Number (line 563)
    reference_number = Column(String(100), unique=True, nullable=False, index=True)

    # Field #2: Status (line 566-567)
    status = Column(String(50), index=True)  # Open, Closed, Awarded, etc.

    # Field #3: Control Number (line 577) - NEWLY ADDED
    control_number = Column(String(100), index=True)

    # Field #4: Approved Budget of Contract (line 579-580)
    approved_budget = Column(Float)

    # Field #6: Bid Form Fee (line 698-699) - NEWLY ADDED
    bid_form_fee = Column(Float, default=0.0)

    # Field #7: Project Name (line 608, 616-617)
    title = Column(String(500))

    # Field #8: Description (line 627-659)
    description = Column(Text)

    # Field #9: Classification (line 583)
    classification = Column(String(100))  # Goods, Services, Infrastructure

    # Field #10: Business Category (line 587)
    category = Column(String(200))

    # Field #11: Procurement Mode (line 582) - NEWLY ADDED
    procurement_mode = Column(String(100))  # Public Bidding, Limited Source, etc.

    # Field #12: Applicable Procurement Rules (line 584) - NEWLY ADDED
    procurement_rules = Column(String(200))

    # Field #13: Lot Type (line 578) - NEWLY ADDED
    lot_type = Column(String(50))  # Single Lot, Multiple Lots

    # TIMELINE FIELDS (🔴🟡 Priority)

    # Field #14: Published Date (line 692)
    publish_date = Column(DateTime, index=True)

    # Field #15: Closing Date (line 694) - CRITICAL
    closing_date = Column(DateTime, index=True, nullable=True)

    # Field #16: Date Last Updated (line 695) - NEWLY ADDED
    date_last_updated = Column(DateTime)

    # Field #17: Bid Validity Period (line 575-576) - NEWLY ADDED
    bid_validity_days = Column(Integer)

    # Field #18: Date Created (line 592) - NEWLY ADDED
    date_created = Column(DateTime)

    # DELIVERY & LOCATION FIELDS (🔴 Priority)

    # Field #19: Delivery Period (line 588)
    delivery_period = Column(String(200))  # e.g., "30 Day(s)"

    # Field #20: Delivery/Project Location (line 586) - NEWLY ADDED
    delivery_location = Column(String(300))  # e.g., "Cavite"

    # Field #21: Agency Address (lines 601-604) - NEWLY ADDED
    agency_address = Column(Text)  # Full address

    # CLIENT/AGENCY INFORMATION (🟡 Priority)

    # Field #22: Client Agency (line 589, 598)
    procuring_entity = Column(String(300))

    # Field #23: Contact Person (line 590)
    contact_person = Column(String(200))

    # Related to Field #23
    contact_email = Column(String(200))
    contact_phone = Column(String(100))

    # Field #24: Created By (line 591) - NEWLY ADDED
    created_by = Column(String(200))

    # FUNDING (🟡 Priority)

    # Field #25: Funding Source (line 585) - NEWLY ADDED
    funding_source = Column(String(300))

    # TRACKING & META (🟢 Priority)

    # Field #35: Number of Downloads (line 706-707) - NEWLY ADDED
    download_count = Column(Integer, default=0)

    # Document URL
    url = Column(String(500))

    # Scraper metadata
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships (Field #26: Line Items)
    line_items = relationship("LineItem", back_populates="bid_notice", cascade="all, delete-orphan")
    activity_schedule = relationship("ActivitySchedule", back_populates="bid_notice", cascade="all, delete-orphan")
    bid_supplements = relationship("BidSupplement", back_populates="bid_notice", cascade="all, delete-orphan")
    documents = relationship("BidDocument", back_populates="bid_notice", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BidNotice(reference='{self.reference_number}', title='{self.title[:50]}...')>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'reference_number': self.reference_number,
            'control_number': self.control_number,
            'status': self.status,
            'title': self.title,
            'procuring_entity': self.procuring_entity,
            'classification': self.classification,
            'category': self.category,
            'procurement_mode': self.procurement_mode,
            'procurement_rules': self.procurement_rules,
            'lot_type': self.lot_type,
            'approved_budget': self.approved_budget,
            'bid_form_fee': self.bid_form_fee,
            'bid_validity_days': self.bid_validity_days,
            'publish_date': self.publish_date.isoformat() if self.publish_date else None,
            'closing_date': self.closing_date.isoformat() if self.closing_date else None,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'date_last_updated': self.date_last_updated.isoformat() if self.date_last_updated else None,
            'description': self.description,
            'delivery_period': self.delivery_period,
            'delivery_location': self.delivery_location,
            'agency_address': self.agency_address,
            'contact_person': self.contact_person,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'created_by': self.created_by,
            'funding_source': self.funding_source,
            'download_count': self.download_count,
            'url': self.url,
            'line_items': [item.to_dict() for item in self.line_items] if self.line_items else [],
            'documents': [doc.to_dict() for doc in self.documents] if self.documents else [],
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class LineItem(Base):
    """
    Line items for bid notices - Field #26 from BID_DATA_FIELDS.md

    Location: PS-PhilGEPS_Bid-Notice.html:664-683
    Example: Bid #7297 has 1 line item (200 Pax delivered meals)
    """

    __tablename__ = 'line_items'

    id = Column(Integer, primary_key=True)
    bid_notice_id = Column(Integer, ForeignKey('bid_notices.id'), nullable=False)

    item_number = Column(Integer)  # Sequential number
    unspsc_code = Column(String(50))  # Universal product/service code (e.g., "90101802")
    lot_name = Column(String(300))  # e.g., "Delivered meals services"
    lot_description = Column(Text)
    quantity = Column(Float)  # e.g., 200
    unit_of_measure = Column(String(50))  # e.g., "Pax"

    # Relationship
    bid_notice = relationship("BidNotice", back_populates="line_items")

    def to_dict(self):
        return {
            'item_number': self.item_number,
            'unspsc_code': self.unspsc_code,
            'lot_name': self.lot_name,
            'lot_description': self.lot_description,
            'quantity': self.quantity,
            'unit_of_measure': self.unit_of_measure,
        }


class ActivitySchedule(Base):
    """
    Schedule of activity - Field #29 from BID_DATA_FIELDS.md

    Location: PS-PhilGEPS_Bid-Notice.html:691
    Examples: Pre-bid conference, submission deadline, bid opening
    """

    __tablename__ = 'activity_schedules'

    id = Column(Integer, primary_key=True)
    bid_notice_id = Column(Integer, ForeignKey('bid_notices.id'), nullable=False)

    activity_type = Column(String(100))  # Pre-bid, Submission, Opening, etc.
    scheduled_date = Column(DateTime)
    location = Column(String(300))
    description = Column(Text)

    # Relationship
    bid_notice = relationship("BidNotice", back_populates="activity_schedule")

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'activity_type': self.activity_type,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'location': self.location,
            'description': self.description,
        }


class BidSupplement(Base):
    """
    Bid supplements (amendments) - Field #32 from BID_DATA_FIELDS.md

    Location: PS-PhilGEPS_Bid-Notice.html:700-701
    Purpose: Track changes/amendments to original bid notice
    """

    __tablename__ = 'bid_supplements'

    id = Column(Integer, primary_key=True)
    bid_notice_id = Column(Integer, ForeignKey('bid_notices.id'), nullable=False)

    supplement_number = Column(Integer)
    amendment_type = Column(String(100))
    description = Column(Text)
    issued_date = Column(DateTime)

    # Relationship
    bid_notice = relationship("BidNotice", back_populates="bid_supplements")

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'supplement_number': self.supplement_number,
            'amendment_type': self.amendment_type,
            'description': self.description,
            'issued_date': self.issued_date.isoformat() if self.issued_date else None,
        }


class BidDocument(Base):
    """
    Bid documents (PDF files from preview page)

    Location: /Tenders/tender_doc_view/{bid_id}/{bid_id}
    Purpose: Store PDF document URLs associated with bid notices
    Note: These URLs require PhilGEPS login to access
    """

    __tablename__ = 'bid_documents'

    id = Column(Integer, primary_key=True)
    bid_notice_id = Column(Integer, ForeignKey('bid_notices.id'), nullable=False)

    filename = Column(String(500))  # e.g., "1762836649_25750220105pr.pdf"
    document_url = Column(String(1000), nullable=False)  # Full URL to PDF
    document_type = Column(String(100))  # e.g., "Bid Notice", "Technical Specs", etc.
    file_size = Column(Integer)  # Optional: file size in bytes
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    bid_notice = relationship("BidNotice", back_populates="documents")

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'filename': self.filename,
            'document_url': self.document_url,
            'document_type': self.document_type,
            'file_size': self.file_size,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
        }


class AwardedContract(Base):
    """
    Awarded Contract model - tracks contracts that have been awarded.

    This is different from BidNotice which tracks open bids.
    AwardedContract tracks the final outcome: who won, for how much, etc.

    Data Source:
    - Index: https://philgeps.gov.ph/Indexes/viewMoreAward
    - Detail: /Indexes/viewAwardNotice/{award_id}/MORE
    """

    __tablename__ = 'awarded_contracts'

    # Meta fields
    id = Column(Integer, primary_key=True, autoincrement=True)

    # PRIMARY IDENTIFIER
    award_notice_number = Column(String(100), unique=True, nullable=False, index=True)  # e.g., "1998"

    # LINK TO ORIGINAL BID
    bid_reference_number = Column(String(100), index=True)  # Links to BidNotice.reference_number (e.g., "6793")
    control_number = Column(String(100), index=True)  # e.g., "2510239"

    # AWARD INFORMATION (CRITICAL FIELDS)
    award_title = Column(String(500))  # e.g., "Various Electromagnetic Flowmeter"
    award_type = Column(String(100))  # e.g., "Award Notice"
    award_date = Column(DateTime, index=True)  # When the contract was awarded

    # AWARDEE (WINNER) INFORMATION
    awardee_name = Column(String(300), index=True)  # e.g., "LOUISE AND AEDAN ENTERPRISE INC."
    awardee_address = Column(Text)  # Full address of winner
    awardee_contact_person = Column(String(200))  # Contact person at winning company
    awardee_corporate_title = Column(String(100))  # e.g., "Proprietor", "CEO"

    # FINANCIAL INFORMATION (KEY FIELDS FOR ANALYSIS)
    approved_budget = Column(Float)  # ABC - Approved Budget for Contract (e.g., PHP 1,375,000.00)
    contract_amount = Column(Float, index=True)  # AWARDED PRICE - What they actually won for (e.g., PHP 750,000.00)

    # CONTRACT DETAILS
    contract_number = Column(String(100))  # Official contract number
    contract_effectivity_date = Column(DateTime)  # When contract starts
    contract_end_date = Column(DateTime)  # When contract ends
    period_of_contract = Column(String(100))  # e.g., "30-Day(s)"
    proceed_date = Column(DateTime)  # Date to proceed

    # PROCUREMENT DETAILS (from original bid)
    procurement_mode = Column(String(100))  # e.g., "Small Value Procurement"
    classification = Column(String(100))  # Goods, Services, Infrastructure
    category = Column(String(200))  # Business category
    procurement_rules = Column(String(200))  # Applicable rules
    funding_source = Column(String(300))  # Source of funds

    # PROCURING ENTITY (BUYER)
    procuring_entity = Column(String(300))  # Government agency
    agency_address = Column(Text)  # Agency address
    delivery_location = Column(String(300))  # Where goods/services delivered

    # TIMELINE FIELDS
    publish_date = Column(DateTime, index=True)  # When award notice was published
    date_created = Column(DateTime)  # When record was created in PhilGEPS
    date_last_updated = Column(DateTime)  # Last update in PhilGEPS

    # DESCRIPTION
    description = Column(Text)  # Detailed description

    # ADDITIONAL INFO
    created_by = Column(String(200))  # PhilGEPS user who created the award notice

    # METADATA
    url = Column(String(500))  # Source URL
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # RELATIONSHIPS
    line_items = relationship("AwardLineItem", back_populates="awarded_contract", cascade="all, delete-orphan")
    documents = relationship("AwardDocument", back_populates="awarded_contract", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AwardedContract(award_number='{self.award_notice_number}', awardee='{self.awardee_name}')>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'award_notice_number': self.award_notice_number,
            'bid_reference_number': self.bid_reference_number,
            'control_number': self.control_number,
            'award_title': self.award_title,
            'award_type': self.award_type,
            'award_date': self.award_date.isoformat() if self.award_date else None,
            'awardee_name': self.awardee_name,
            'awardee_address': self.awardee_address,
            'awardee_contact_person': self.awardee_contact_person,
            'awardee_corporate_title': self.awardee_corporate_title,
            'approved_budget': self.approved_budget,
            'contract_amount': self.contract_amount,
            'contract_number': self.contract_number,
            'contract_effectivity_date': self.contract_effectivity_date.isoformat() if self.contract_effectivity_date else None,
            'contract_end_date': self.contract_end_date.isoformat() if self.contract_end_date else None,
            'period_of_contract': self.period_of_contract,
            'proceed_date': self.proceed_date.isoformat() if self.proceed_date else None,
            'procurement_mode': self.procurement_mode,
            'classification': self.classification,
            'category': self.category,
            'procurement_rules': self.procurement_rules,
            'funding_source': self.funding_source,
            'procuring_entity': self.procuring_entity,
            'agency_address': self.agency_address,
            'delivery_location': self.delivery_location,
            'publish_date': self.publish_date.isoformat() if self.publish_date else None,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'date_last_updated': self.date_last_updated.isoformat() if self.date_last_updated else None,
            'description': self.description,
            'created_by': self.created_by,
            'url': self.url,
            'line_items': [item.to_dict() for item in self.line_items] if self.line_items else [],
            'documents': [doc.to_dict() for doc in self.documents] if self.documents else [],
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_savings_amount(self):
        """Calculate savings amount (ABC - Contract Amount)."""
        if self.approved_budget and self.contract_amount:
            return self.approved_budget - self.contract_amount
        return None

    def get_savings_percentage(self):
        """Calculate savings percentage."""
        if self.approved_budget and self.contract_amount and self.approved_budget > 0:
            return ((self.approved_budget - self.contract_amount) / self.approved_budget) * 100
        return None


class AwardLineItem(Base):
    """
    Line items for awarded contracts.
    Similar to LineItem but for awarded contracts.
    """

    __tablename__ = 'award_line_items'

    id = Column(Integer, primary_key=True)
    awarded_contract_id = Column(Integer, ForeignKey('awarded_contracts.id'), nullable=False)

    item_number = Column(Integer)
    unspsc_code = Column(String(50))
    lot_name = Column(String(300))
    lot_description = Column(Text)
    quantity = Column(Float)
    unit_of_measure = Column(String(50))

    # Relationship
    awarded_contract = relationship("AwardedContract", back_populates="line_items")

    def to_dict(self):
        return {
            'item_number': self.item_number,
            'unspsc_code': self.unspsc_code,
            'lot_name': self.lot_name,
            'lot_description': self.lot_description,
            'quantity': self.quantity,
            'unit_of_measure': self.unit_of_measure,
        }


class AwardDocument(Base):
    """
    Documents for awarded contracts.
    Similar to BidDocument but for awarded contracts.
    """

    __tablename__ = 'award_documents'

    id = Column(Integer, primary_key=True)
    awarded_contract_id = Column(Integer, ForeignKey('awarded_contracts.id'), nullable=False)

    filename = Column(String(500))
    document_url = Column(String(1000), nullable=False)
    document_type = Column(String(100))
    file_size = Column(Integer)
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    awarded_contract = relationship("AwardedContract", back_populates="documents")

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'document_url': self.document_url,
            'document_type': self.document_type,
            'file_size': self.file_size,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
        }


class ScrapingLog(Base):
    """Scraping Log model - tracks scraping sessions."""

    __tablename__ = 'scraping_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_seconds = Column(Float)
    total_scraped = Column(Integer, default=0)
    new_records = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    success = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<ScrapingLog(start='{self.start_time}', scraped={self.total_scraped}, success={self.success})>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'total_scraped': self.total_scraped,
            'new_records': self.new_records,
            'errors': self.errors,
            'success': self.success,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
