"""
Sync Manager Module - Handles synchronization of data with external APIs
"""
import logging
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import Representative, Bill, Vote, ApiConfig
from congress_api import CongressAPI
from config import is_api_configured

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyncManager:
    """
    Manages the synchronization of data between the application database
    and external data sources like the Congress API.
    """
    
    def __init__(self, db: Session):
        """Initialize the sync manager."""
        self.db = db
        self.congress_api = CongressAPI(db)
        
    async def sync_representatives(self, force: bool = False):
        """
        Synchronize representatives data from the Congress API.
        
        Args:
            force (bool): Force synchronization regardless of last update time
        
        Returns:
            dict: Summary of the synchronization results
        """
        if not is_api_configured():
            logger.warning("Congress API not configured. Skipping representatives sync.")
            return {"status": "error", "message": "API not configured"}
            
        logger.info("Starting representatives synchronization...")
        
        # Determine if sync is needed
        last_updated = self.db.query(Representative).order_by(
            Representative.last_updated.desc()
        ).first()
        
        # Skip sync if updated recently (within 24 hours) unless forced
        if last_updated and not force:
            if datetime.utcnow() - last_updated.last_updated < timedelta(days=1):
                logger.info("Representatives data already up to date.")
                return {
                    "status": "skipped", 
                    "message": "Data already up to date",
                    "last_updated": last_updated.last_updated.isoformat()
                }
        
        try:
            # Get current congress members from API
            house_members = await self.congress_api.get_house_members()
            senate_members = await self.congress_api.get_senate_members()
            
            # Process and update database
            updated_count = 0
            new_count = 0
            
            # Process all members
            all_members = house_members + senate_members
            for member_data in all_members:
                congress_id = member_data.get("id")
                if not congress_id:
                    continue
                    
                # Check if member exists
                member = self.db.query(Representative).filter_by(
                    congress_id=congress_id
                ).first()
                
                if member:
                    # Update existing record
                    member.name = member_data.get("name", member.name)
                    member.state = member_data.get("state", member.state)
                    member.district = member_data.get("district", member.district)
                    member.party = member_data.get("party", member.party)
                    member.chamber = "house" if member_data.get("chamber") == "House" else "senate"
                    member.last_updated = datetime.utcnow()
                    updated_count += 1
                else:
                    # Create new record
                    new_member = Representative(
                        congress_id=congress_id,
                        name=member_data.get("name", ""),
                        state=member_data.get("state", ""),
                        district=member_data.get("district", ""),
                        party=member_data.get("party", ""),
                        chamber="house" if member_data.get("chamber") == "House" else "senate",
                        last_updated=datetime.utcnow()
                    )
                    self.db.add(new_member)
                    new_count += 1
            
            # Commit changes
            self.db.commit()
            
            logger.info(f"Representatives sync completed: {new_count} new, {updated_count} updated")
            return {
                "status": "success",
                "new_records": new_count,
                "updated_records": updated_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error syncing representatives: {e}")
            self.db.rollback()
            return {"status": "error", "message": str(e)}
    
    async def sync_recent_bills(self, limit: int = 100, force: bool = False):
        """
        Synchronize recent bills data from the Congress API.
        
        Args:
            limit (int): Maximum number of bills to sync
            force (bool): Force synchronization regardless of last update time
        
        Returns:
            dict: Summary of the synchronization results
        """
        if not is_api_configured():
            logger.warning("Congress API not configured. Skipping bills sync.")
            return {"status": "error", "message": "API not configured"}
            
        logger.info(f"Starting recent bills synchronization (limit: {limit})...")
        
        # Determine if sync is needed
        last_updated = self.db.query(Bill).order_by(
            Bill.last_updated.desc()
        ).first()
        
        # Skip sync if updated recently (within 6 hours) unless forced
        if last_updated and not force:
            if datetime.utcnow() - last_updated.last_updated < timedelta(hours=6):
                logger.info("Bills data already up to date.")
                return {
                    "status": "skipped", 
                    "message": "Data already up to date",
                    "last_updated": last_updated.last_updated.isoformat()
                }
        
        try:
            # Get recent bills from API
            recent_bills = await self.congress_api.get_recent_bills(limit=limit)
            
            # Process and update database
            updated_count = 0
            new_count = 0
            
            for bill_data in recent_bills:
                congress_id = bill_data.get("bill_id")
                if not congress_id:
                    continue
                    
                # Check if bill exists
                bill = self.db.query(Bill).filter_by(
                    congress_id=congress_id
                ).first()
                
                if bill:
                    # Update existing record
                    bill.title = bill_data.get("title", bill.title)
                    bill.introduced_date = bill_data.get("introduced_date", bill.introduced_date)
                    bill.status = bill_data.get("status", bill.status)
                    bill.url = bill_data.get("url", bill.url)
                    bill.last_updated = datetime.utcnow()
                    updated_count += 1
                else:
                    # Create new record
                    new_bill = Bill(
                        congress_id=congress_id,
                        title=bill_data.get("title", ""),
                        introduced_date=bill_data.get("introduced_date"),
                        status=bill_data.get("status", ""),
                        url=bill_data.get("url", ""),
                        last_updated=datetime.utcnow()
                    )
                    self.db.add(new_bill)
                    new_count += 1
            
            # Commit changes
            self.db.commit()
            
            logger.info(f"Bills sync completed: {new_count} new, {updated_count} updated")
            return {
                "status": "success",
                "new_records": new_count,
                "updated_records": updated_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error syncing bills: {e}")
            self.db.rollback()
            return {"status": "error", "message": str(e)}
    
    async def sync_recent_votes(self, limit: int = 50, force: bool = False):
        """
        Synchronize recent votes data from the Congress API.
        
        Args:
            limit (int): Maximum number of votes to sync
            force (bool): Force synchronization regardless of last update time
        
        Returns:
            dict: Summary of the synchronization results
        """
        if not is_api_configured():
            logger.warning("Congress API not configured. Skipping votes sync.")
            return {"status": "error", "message": "API not configured"}
            
        logger.info(f"Starting recent votes synchronization (limit: {limit})...")
        
        # Determine if sync is needed
        last_updated = self.db.query(Vote).order_by(
            Vote.last_updated.desc()
        ).first()
        
        # Skip sync if updated recently (within 6 hours) unless forced
        if last_updated and not force:
            if datetime.utcnow() - last_updated.last_updated < timedelta(hours=6):
                logger.info("Votes data already up to date.")
                return {
                    "status": "skipped", 
                    "message": "Data already up to date",
                    "last_updated": last_updated.last_updated.isoformat()
                }
        
        try:
            # Get recent votes from API
            recent_votes = await self.congress_api.get_recent_votes(limit=limit)
            
            # Process and update database
            updated_count = 0
            new_count = 0
            
            for vote_data in recent_votes:
                congress_vote_id = vote_data.get("vote_id")
                if not congress_vote_id:
                    continue
                
                # Get related bill
                bill_id = vote_data.get("bill_id")
                bill = None
                if bill_id:
                    bill = self.db.query(Bill).filter_by(congress_id=bill_id).first()
                    
                    # If bill doesn't exist, create a placeholder
                    if not bill and bill_id:
                        bill = Bill(
                            congress_id=bill_id,
                            title=vote_data.get("bill_title", ""),
                            status="placeholder",
                            last_updated=datetime.utcnow()
                        )
                        self.db.add(bill)
                        self.db.flush()  # Get the ID without committing
                
                # Check if vote exists
                vote = self.db.query(Vote).filter_by(
                    congress_vote_id=congress_vote_id
                ).first()
                
                if vote:
                    # Update existing record
                    vote.bill_id = bill.id if bill else vote.bill_id
                    vote.vote_date = vote_data.get("vote_date", vote.vote_date)
                    vote.question = vote_data.get("question", vote.question)
                    vote.result = vote_data.get("result", vote.result)
                    vote.chamber = vote_data.get("chamber", vote.chamber).lower()
                    vote.last_updated = datetime.utcnow()
                    updated_count += 1
                else:
                    # Create new record
                    new_vote = Vote(
                        congress_vote_id=congress_vote_id,
                        bill_id=bill.id if bill else None,
                        vote_date=vote_data.get("vote_date"),
                        question=vote_data.get("question", ""),
                        result=vote_data.get("result", ""),
                        chamber=vote_data.get("chamber", "").lower(),
                        last_updated=datetime.utcnow()
                    )
                    self.db.add(new_vote)
                    new_count += 1
            
            # Commit changes
            self.db.commit()
            
            logger.info(f"Votes sync completed: {new_count} new, {updated_count} updated")
            return {
                "status": "success",
                "new_records": new_count,
                "updated_records": updated_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error syncing votes: {e}")
            self.db.rollback()
            return {"status": "error", "message": str(e)}
            
    async def run_full_sync(self, force: bool = False):
        """
        Run a full synchronization of all data from the Congress API.
        
        Args:
            force (bool): Force synchronization regardless of last update time
        
        Returns:
            dict: Summary of the synchronization results
        """
        logger.info("Starting full data synchronization...")
        
        results = {
            "representatives": await self.sync_representatives(force),
            "bills": await self.sync_recent_bills(limit=200, force=force),
            "votes": await self.sync_recent_votes(limit=100, force=force)
        }
        
        return {
            "status": "completed",
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }

# Function to get a sync manager instance
def get_sync_manager(db: Session):
    """
    Get a sync manager instance.
    
    Args:
        db (Session): Database session
        
    Returns:
        SyncManager: Instance of the sync manager
    """
    return SyncManager(db) 