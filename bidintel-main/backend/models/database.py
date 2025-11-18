"""Database connection and operations."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from models.schemas import Base, BidNotice, ScrapingLog, LineItem, BidDocument, AwardedContract, AwardLineItem, AwardDocument
from config.settings import settings
from utils.logger import logger
from typing import Optional, List, Dict
from datetime import datetime


class Database:
    """Database manager for PhilGEPS scraper."""

    def __init__(self):
        """Initialize database connection."""
        self.engine = create_engine(settings.DATABASE_URL, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._create_tables()

    def _create_tables(self):
        """Create all tables if they don't exist."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise

    def get_session(self) -> Session:
        """
        Get a new database session.

        Returns:
            Session: SQLAlchemy session
        """
        return self.SessionLocal()

    def save_bid_notice(self, bid_data: Dict) -> Optional[BidNotice]:
        """
        Save or update a bid notice.

        Args:
            bid_data: Dictionary containing bid notice data

        Returns:
            BidNotice: Saved bid notice instance or None
        """
        session = self.get_session()
        try:
            # Extract line_items and documents from bid_data to handle separately
            line_items_data = bid_data.pop('line_items', [])
            documents_data = bid_data.pop('documents', [])

            # Check if already exists
            existing = session.query(BidNotice).filter_by(
                reference_number=bid_data['reference_number']
            ).first()

            if existing:
                # Update existing record
                for key, value in bid_data.items():
                    if hasattr(existing, key) and key not in ['line_items', 'documents']:
                        setattr(existing, key, value)

                # Clear and update line items
                existing.line_items.clear()
                for item_data in line_items_data:
                    line_item = LineItem(**item_data)
                    existing.line_items.append(line_item)

                # Clear and update documents
                existing.documents.clear()
                for doc_data in documents_data:
                    document = BidDocument(**doc_data)
                    existing.documents.append(document)

                logger.debug(f"Updated bid: {bid_data['reference_number']}")
                bid_notice = existing
            else:
                # Create new record without line_items and documents
                bid_notice = BidNotice(**bid_data)
                session.add(bid_notice)

                # Add line items as ORM instances
                for item_data in line_items_data:
                    line_item = LineItem(**item_data)
                    bid_notice.line_items.append(line_item)

                # Add documents as ORM instances
                for doc_data in documents_data:
                    document = BidDocument(**doc_data)
                    bid_notice.documents.append(document)

                logger.debug(f"Created new bid: {bid_data['reference_number']}")

            session.commit()
            session.refresh(bid_notice)
            return bid_notice

        except IntegrityError as e:
            session.rollback()
            logger.error(f"Integrity error saving bid: {str(e)}")
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving bid notice: {str(e)}")
            return None
        finally:
            session.close()

    def bid_exists(self, reference_number: str) -> bool:
        """
        Check if bid notice already exists in database.

        Args:
            reference_number: Bid reference number

        Returns:
            bool: True if exists, False otherwise
        """
        session = self.get_session()
        try:
            exists = session.query(BidNotice).filter_by(
                reference_number=reference_number
            ).first() is not None
            return exists
        finally:
            session.close()

    def get_bid_by_reference(self, reference_number: str) -> Optional[BidNotice]:
        """
        Get bid notice by reference number.

        Args:
            reference_number: Bid reference number

        Returns:
            BidNotice: Bid notice instance or None
        """
        session = self.get_session()
        try:
            return session.query(BidNotice).filter_by(
                reference_number=reference_number
            ).first()
        finally:
            session.close()

    def get_all_bids(self, limit: int = 100, filters: Dict = None) -> List[BidNotice]:
        """
        Get all bid notices with optional filtering.

        Args:
            limit: Maximum number of records to return
            filters: Optional dictionary of filters

        Returns:
            list: List of BidNotice instances
        """
        session = self.get_session()
        try:
            query = session.query(BidNotice)

            # Apply filters if provided
            if filters:
                query = self._apply_filters(query, filters)

            return query.order_by(
                BidNotice.scraped_at.desc()
            ).limit(limit).all()
        finally:
            session.close()

    def get_filtered_bids(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        min_budget: Optional[float] = None,
        max_budget: Optional[float] = None,
        classification: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        search_term: Optional[str] = None,
        limit: int = 100
    ) -> List[BidNotice]:
        """
        Get bid notices with comprehensive filtering.

        Args:
            date_from: Filter bids published/closing from this date
            date_to: Filter bids published/closing until this date
            min_budget: Minimum approved budget
            max_budget: Maximum approved budget
            classification: Filter by classification (Goods, Services, Infrastructure)
            category: Filter by business category
            status: Filter by status (Open, Closed, Awarded, etc.)
            search_term: Search in title and description
            limit: Maximum number of records to return

        Returns:
            list: List of filtered BidNotice instances
        """
        session = self.get_session()
        try:
            query = session.query(BidNotice)

            # Date filters (checking both publish_date and closing_date)
            if date_from:
                query = query.filter(
                    (BidNotice.publish_date >= date_from) |
                    (BidNotice.closing_date >= date_from)
                )

            if date_to:
                query = query.filter(
                    (BidNotice.publish_date <= date_to) |
                    (BidNotice.closing_date <= date_to)
                )

            # Budget filters
            if min_budget is not None:
                query = query.filter(BidNotice.approved_budget >= min_budget)

            if max_budget is not None:
                query = query.filter(BidNotice.approved_budget <= max_budget)

            # Classification filter
            if classification:
                query = query.filter(
                    BidNotice.classification.ilike(f'%{classification}%')
                )

            # Category filter
            if category:
                query = query.filter(
                    BidNotice.category.ilike(f'%{category}%')
                )

            # Status filter
            if status:
                query = query.filter(BidNotice.status.ilike(f'%{status}%'))

            # Search term (searches title and description)
            if search_term:
                search_pattern = f'%{search_term}%'
                query = query.filter(
                    (BidNotice.title.ilike(search_pattern)) |
                    (BidNotice.description.ilike(search_pattern))
                )

            return query.order_by(
                BidNotice.closing_date.desc()
            ).limit(limit).all()

        finally:
            session.close()

    def _apply_filters(self, query, filters: Dict):
        """
        Apply filter dictionary to query.

        Args:
            query: SQLAlchemy query object
            filters: Dictionary of filter key-value pairs

        Returns:
            Modified query object
        """
        for key, value in filters.items():
            if value is None:
                continue

            if key == 'date_from':
                query = query.filter(BidNotice.publish_date >= value)
            elif key == 'date_to':
                query = query.filter(BidNotice.publish_date <= value)
            elif key == 'min_budget':
                query = query.filter(BidNotice.approved_budget >= value)
            elif key == 'max_budget':
                query = query.filter(BidNotice.approved_budget <= value)
            elif key == 'classification':
                query = query.filter(BidNotice.classification.ilike(f'%{value}%'))
            elif key == 'category':
                query = query.filter(BidNotice.category.ilike(f'%{value}%'))
            elif key == 'status':
                query = query.filter(BidNotice.status.ilike(f'%{value}%'))
            elif key == 'search':
                query = query.filter(
                    (BidNotice.title.ilike(f'%{value}%')) |
                    (BidNotice.description.ilike(f'%{value}%'))
                )

        return query

    def get_active_bids(self) -> List[BidNotice]:
        """
        Get all active/open bid notices.

        Returns:
            list: List of active BidNotice instances
        """
        session = self.get_session()
        try:
            return session.query(BidNotice).filter(
                BidNotice.status.in_(['Open', 'Active'])
            ).order_by(BidNotice.closing_date).all()
        finally:
            session.close()

    def save_scraping_log(self, log_entry: ScrapingLog) -> Optional[ScrapingLog]:
        """
        Save a scraping log entry.

        Args:
            log_entry: ScrapingLog instance

        Returns:
            ScrapingLog: Saved log entry or None
        """
        session = self.get_session()
        try:
            session.add(log_entry)
            session.commit()
            session.refresh(log_entry)
            return log_entry
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving scraping log: {str(e)}")
            return None
        finally:
            session.close()

    def get_recent_logs(self, limit: int = 10) -> List[ScrapingLog]:
        """
        Get recent scraping logs.

        Args:
            limit: Maximum number of logs to return

        Returns:
            list: List of ScrapingLog instances
        """
        session = self.get_session()
        try:
            return session.query(ScrapingLog).order_by(
                ScrapingLog.start_time.desc()
            ).limit(limit).all()
        finally:
            session.close()

    def get_stats(self) -> Dict:
        """
        Get database statistics.

        Returns:
            dict: Statistics about scraped data
        """
        session = self.get_session()
        try:
            total_bids = session.query(BidNotice).count()
            active_bids = session.query(BidNotice).filter(
                BidNotice.status.in_(['Open', 'Active'])
            ).count()
            total_scrapes = session.query(ScrapingLog).count()
            successful_scrapes = session.query(ScrapingLog).filter(
                ScrapingLog.success == True
            ).count()

            return {
                'total_bids': total_bids,
                'active_bids': active_bids,
                'total_scraping_sessions': total_scrapes,
                'successful_sessions': successful_scrapes
            }
        finally:
            session.close()

    # =========================================================================
    # AWARDED CONTRACTS METHODS
    # =========================================================================

    def save_awarded_contract(self, award_data: Dict) -> Optional[AwardedContract]:
        """
        Save or update an awarded contract.

        Args:
            award_data: Dictionary containing awarded contract data

        Returns:
            AwardedContract: Saved awarded contract instance or None
        """
        session = self.get_session()
        try:
            # Extract line_items and documents from award_data to handle separately
            line_items_data = award_data.pop('line_items', [])
            documents_data = award_data.pop('documents', [])

            # Check if already exists
            existing = session.query(AwardedContract).filter_by(
                award_notice_number=award_data['award_notice_number']
            ).first()

            if existing:
                # Update existing record
                for key, value in award_data.items():
                    if hasattr(existing, key) and key not in ['line_items', 'documents']:
                        setattr(existing, key, value)

                # Clear and update line items
                existing.line_items.clear()
                for item_data in line_items_data:
                    line_item = AwardLineItem(**item_data)
                    existing.line_items.append(line_item)

                # Clear and update documents
                existing.documents.clear()
                for doc_data in documents_data:
                    document = AwardDocument(**doc_data)
                    existing.documents.append(document)

                logger.debug(f"Updated awarded contract: {award_data['award_notice_number']}")
                awarded_contract = existing
            else:
                # Create new record without line_items and documents
                awarded_contract = AwardedContract(**award_data)
                session.add(awarded_contract)

                # Add line items as ORM instances
                for item_data in line_items_data:
                    line_item = AwardLineItem(**item_data)
                    awarded_contract.line_items.append(line_item)

                # Add documents as ORM instances
                for doc_data in documents_data:
                    document = AwardDocument(**doc_data)
                    awarded_contract.documents.append(document)

                logger.debug(f"Created new awarded contract: {award_data['award_notice_number']}")

            session.commit()
            session.refresh(awarded_contract)
            return awarded_contract

        except IntegrityError as e:
            session.rollback()
            logger.error(f"Integrity error saving awarded contract: {str(e)}")
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving awarded contract: {str(e)}")
            return None
        finally:
            session.close()

    def awarded_contract_exists(self, award_notice_number: str) -> bool:
        """
        Check if awarded contract already exists in database.

        Args:
            award_notice_number: Award notice number

        Returns:
            bool: True if exists, False otherwise
        """
        session = self.get_session()
        try:
            exists = session.query(AwardedContract).filter_by(
                award_notice_number=award_notice_number
            ).first() is not None
            return exists
        finally:
            session.close()

    def get_awarded_contract_by_number(self, award_notice_number: str) -> Optional[AwardedContract]:
        """
        Get awarded contract by award notice number.

        Args:
            award_notice_number: Award notice number

        Returns:
            AwardedContract: Awarded contract instance or None
        """
        session = self.get_session()
        try:
            return session.query(AwardedContract).filter_by(
                award_notice_number=award_notice_number
            ).first()
        finally:
            session.close()

    def get_all_awarded_contracts(self, limit: int = 100, filters: Dict = None) -> List[AwardedContract]:
        """
        Get all awarded contracts with optional filtering.

        Args:
            limit: Maximum number of records to return
            filters: Optional dictionary of filters

        Returns:
            list: List of AwardedContract instances
        """
        session = self.get_session()
        try:
            query = session.query(AwardedContract)

            # Apply filters if provided
            if filters:
                query = self._apply_award_filters(query, filters)

            return query.order_by(
                AwardedContract.award_date.desc()
            ).limit(limit).all()
        finally:
            session.close()

    def get_filtered_awarded_contracts(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        min_budget: Optional[float] = None,
        max_budget: Optional[float] = None,
        min_contract_amount: Optional[float] = None,
        max_contract_amount: Optional[float] = None,
        classification: Optional[str] = None,
        category: Optional[str] = None,
        awardee: Optional[str] = None,
        procuring_entity: Optional[str] = None,
        search_term: Optional[str] = None,
        limit: int = 100
    ) -> List[AwardedContract]:
        """
        Get awarded contracts with comprehensive filtering.

        Args:
            date_from: Filter awards from this date
            date_to: Filter awards until this date
            min_budget: Minimum approved budget (ABC)
            max_budget: Maximum approved budget (ABC)
            min_contract_amount: Minimum contract amount (awarded price)
            max_contract_amount: Maximum contract amount (awarded price)
            classification: Filter by classification (Goods, Services, Infrastructure)
            category: Filter by business category
            awardee: Filter by awardee name
            procuring_entity: Filter by procuring entity
            search_term: Search in title and description
            limit: Maximum number of records to return

        Returns:
            list: List of filtered AwardedContract instances
        """
        session = self.get_session()
        try:
            query = session.query(AwardedContract)

            # Date filters (award_date)
            if date_from:
                query = query.filter(AwardedContract.award_date >= date_from)

            if date_to:
                query = query.filter(AwardedContract.award_date <= date_to)

            # Budget filters (ABC)
            if min_budget is not None:
                query = query.filter(AwardedContract.approved_budget >= min_budget)

            if max_budget is not None:
                query = query.filter(AwardedContract.approved_budget <= max_budget)

            # Contract amount filters (Awarded Price)
            if min_contract_amount is not None:
                query = query.filter(AwardedContract.contract_amount >= min_contract_amount)

            if max_contract_amount is not None:
                query = query.filter(AwardedContract.contract_amount <= max_contract_amount)

            # Classification filter
            if classification:
                query = query.filter(
                    AwardedContract.classification.ilike(f'%{classification}%')
                )

            # Category filter
            if category:
                query = query.filter(
                    AwardedContract.category.ilike(f'%{category}%')
                )

            # Awardee filter
            if awardee:
                query = query.filter(
                    AwardedContract.awardee_name.ilike(f'%{awardee}%')
                )

            # Procuring entity filter
            if procuring_entity:
                query = query.filter(
                    AwardedContract.procuring_entity.ilike(f'%{procuring_entity}%')
                )

            # Search term (searches title and description)
            if search_term:
                search_pattern = f'%{search_term}%'
                query = query.filter(
                    (AwardedContract.award_title.ilike(search_pattern)) |
                    (AwardedContract.description.ilike(search_pattern))
                )

            return query.order_by(
                AwardedContract.award_date.desc()
            ).limit(limit).all()

        finally:
            session.close()

    def _apply_award_filters(self, query, filters: Dict):
        """
        Apply filter dictionary to awarded contracts query.

        Args:
            query: SQLAlchemy query object
            filters: Dictionary of filter key-value pairs

        Returns:
            Modified query object
        """
        for key, value in filters.items():
            if value is None:
                continue

            if key == 'date_from':
                query = query.filter(AwardedContract.award_date >= value)
            elif key == 'date_to':
                query = query.filter(AwardedContract.award_date <= value)
            elif key == 'min_budget':
                query = query.filter(AwardedContract.approved_budget >= value)
            elif key == 'max_budget':
                query = query.filter(AwardedContract.approved_budget <= value)
            elif key == 'min_contract_amount':
                query = query.filter(AwardedContract.contract_amount >= value)
            elif key == 'max_contract_amount':
                query = query.filter(AwardedContract.contract_amount <= value)
            elif key == 'classification':
                query = query.filter(AwardedContract.classification.ilike(f'%{value}%'))
            elif key == 'category':
                query = query.filter(AwardedContract.category.ilike(f'%{value}%'))
            elif key == 'awardee':
                query = query.filter(AwardedContract.awardee_name.ilike(f'%{value}%'))
            elif key == 'procuring_entity':
                query = query.filter(AwardedContract.procuring_entity.ilike(f'%{value}%'))
            elif key == 'search':
                query = query.filter(
                    (AwardedContract.award_title.ilike(f'%{value}%')) |
                    (AwardedContract.description.ilike(f'%{value}%'))
                )

        return query

    def get_awarded_contracts_by_awardee(self, awardee_name: str, limit: int = 100) -> List[AwardedContract]:
        """
        Get all awarded contracts for a specific awardee.

        Args:
            awardee_name: Name of the awardee
            limit: Maximum number of records to return

        Returns:
            list: List of AwardedContract instances
        """
        session = self.get_session()
        try:
            return session.query(AwardedContract).filter(
                AwardedContract.awardee_name.ilike(f'%{awardee_name}%')
            ).order_by(AwardedContract.award_date.desc()).limit(limit).all()
        finally:
            session.close()

    def get_awarded_contracts_by_bid_reference(self, bid_reference_number: str) -> List[AwardedContract]:
        """
        Get awarded contracts linked to a specific bid reference number.

        This allows you to see who won a particular bid opportunity.

        Args:
            bid_reference_number: Bid notice reference number

        Returns:
            list: List of AwardedContract instances
        """
        session = self.get_session()
        try:
            return session.query(AwardedContract).filter(
                AwardedContract.bid_reference_number == bid_reference_number
            ).all()
        finally:
            session.close()

    def get_award_stats(self) -> Dict:
        """
        Get statistics about awarded contracts.

        Returns:
            dict: Statistics about awarded contracts including:
                  - total_awards: Total number of awarded contracts
                  - total_abc: Total approved budgets
                  - total_contract_amount: Total contract amounts (awarded prices)
                  - total_savings: Total savings (ABC - Contract Amount)
                  - avg_savings_percentage: Average savings percentage
        """
        session = self.get_session()
        try:
            from sqlalchemy import func

            total_awards = session.query(AwardedContract).count()

            # Get sum of budgets and contract amounts
            totals = session.query(
                func.sum(AwardedContract.approved_budget).label('total_abc'),
                func.sum(AwardedContract.contract_amount).label('total_contract_amount')
            ).filter(
                AwardedContract.approved_budget.isnot(None),
                AwardedContract.contract_amount.isnot(None)
            ).first()

            total_abc = float(totals.total_abc) if totals.total_abc else 0
            total_contract_amount = float(totals.total_contract_amount) if totals.total_contract_amount else 0
            total_savings = total_abc - total_contract_amount
            avg_savings_percentage = (total_savings / total_abc * 100) if total_abc > 0 else 0

            # Get unique awardees count
            unique_awardees = session.query(
                func.count(func.distinct(AwardedContract.awardee_name))
            ).scalar()

            return {
                'total_awards': total_awards,
                'total_abc': total_abc,
                'total_contract_amount': total_contract_amount,
                'total_savings': total_savings,
                'avg_savings_percentage': avg_savings_percentage,
                'unique_awardees': unique_awardees
            }
        finally:
            session.close()
