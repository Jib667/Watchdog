import logging
import sqlite3
from datetime import datetime

from congress_api import get_api_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Move the import inside the function to avoid circular imports
def get_db_connection():
    """Get a database connection from the server module"""
    from server import get_db_connection as server_get_db_connection
    return server_get_db_connection()

class SyncManager:
    """Manages synchronization between external APIs and the local database."""
    
    def __init__(self):
        """Initialize the SyncManager."""
        self.api_client = get_api_client()
        
    async def sync_representatives(self, force=False):
        """Synchronize representatives data from Congress API to database.
        
        Args:
            force (bool): If True, update all records even if they exist
            
        Returns:
            dict: Count of new and updated records
        """
        logger.info(f"Starting representatives sync (force={force})")
        
        # Fetch representatives from API
        house_members = await self.api_client.get_house_members()
        senate_members = await self.api_client.get_senate_members()
        
        # Combine representatives
        all_members = house_members + senate_members
        logger.info(f"Fetched {len(all_members)} representatives from API")
        
        if not all_members:
            logger.warning("No representatives fetched from API, aborting sync")
            return {"new": 0, "updated": 0, "error": "No data from API"}
        
        # Update database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        new_count = 0
        updated_count = 0
        processed_ids = set()  # Track processed IDs to avoid duplicates
        
        for member in all_members:
            try:
                congress_id = member.get("congress_id")
                
                # Skip if we've already processed this ID in this batch
                if congress_id in processed_ids:
                    logger.warning(f"Skipping duplicate congress_id: {congress_id}")
                    continue
                
                processed_ids.add(congress_id)
                
                # Check if representative already exists
                existing = cursor.execute(
                    "SELECT id FROM representatives WHERE congress_id = ?", 
                    (congress_id,)
                ).fetchone()
                
                if existing and not force:
                    # Update existing record
                    cursor.execute(
                        """
                        UPDATE representatives 
                        SET name = ?, state = ?, district = ?, party = ?, chamber = ?, updated_at = CURRENT_TIMESTAMP 
                        WHERE congress_id = ?
                        """,
                        (member.get("name"), member.get("state"), member.get("district"), 
                         member.get("party"), member.get("chamber"), congress_id)
                    )
                    updated_count += 1
                else:
                    # Insert new record
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO representatives 
                        (congress_id, name, state, district, party, chamber) 
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (congress_id, member.get("name"), member.get("state"), member.get("district"), 
                         member.get("party"), member.get("chamber"))
                    )
                    new_count += 1
            
            except Exception as e:
                logger.error(f"Error syncing representative {member.get('name')}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Representatives sync completed: {new_count} new, {updated_count} updated")
        return {"new": new_count, "updated": updated_count}
    
    async def sync_bills(self, force=False):
        """Synchronize bills data from Congress API to database.
        
        Args:
            force (bool): If True, update all records even if they exist
            
        Returns:
            dict: Count of new and updated records
        """
        logger.info(f"Starting bills sync (force={force})")
        
        # Fetch bills from API
        bills = await self.api_client.get_recent_bills(limit=50)
        logger.info(f"Fetched {len(bills)} bills from API")
        
        if not bills:
            logger.warning("No bills fetched from API, aborting sync")
            return {"new": 0, "updated": 0, "error": "No data from API"}
        
        # Update database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        new_count = 0
        updated_count = 0
        
        for bill in bills:
            try:
                bill_id = bill.get("bill_id")
                
                # Check if bill already exists
                existing = cursor.execute(
                    "SELECT id FROM bills WHERE bill_id = ?", 
                    (bill_id,)
                ).fetchone()
                
                if existing and not force:
                    # Update existing record
                    cursor.execute(
                        """
                        UPDATE bills 
                        SET title = ?, introduced_date = ?, status = ?, url = ?, sponsor = ?, updated_at = CURRENT_TIMESTAMP 
                        WHERE bill_id = ?
                        """,
                        (bill.get("title"), bill.get("introduced_date"), bill.get("status"), 
                         bill.get("url"), bill.get("sponsor"), bill_id)
                    )
                    updated_count += 1
                else:
                    # Insert new record
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO bills 
                        (bill_id, title, introduced_date, status, url, sponsor) 
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (bill_id, bill.get("title"), bill.get("introduced_date"), bill.get("status"), 
                         bill.get("url"), bill.get("sponsor"))
                    )
                    new_count += 1
            
            except Exception as e:
                logger.error(f"Error syncing bill {bill.get('bill_id')}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Bills sync completed: {new_count} new, {updated_count} updated")
        return {"new": new_count, "updated": updated_count}
    
    async def sync_votes(self, force=False):
        """Synchronize votes data from Congress API to database.
        
        Args:
            force (bool): If True, update all records even if they exist
            
        Returns:
            dict: Count of new and updated records
        """
        logger.info(f"Starting votes sync (force={force})")
        
        # Fetch votes from API
        votes = await self.api_client.get_recent_votes(limit=50)
        logger.info(f"Fetched {len(votes)} votes from API")
        
        if not votes:
            logger.warning("No votes fetched from API, aborting sync")
            return {"new": 0, "updated": 0, "error": "No data from API"}
        
        # Update database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        new_count = 0
        updated_count = 0
        
        for vote in votes:
            try:
                vote_id = vote.get("vote_id")
                
                # Check if vote already exists
                existing = cursor.execute(
                    "SELECT id FROM votes WHERE vote_id = ?", 
                    (vote_id,)
                ).fetchone()
                
                if existing and not force:
                    # Update existing record
                    cursor.execute(
                        """
                        UPDATE votes 
                        SET bill_id = ?, bill_title = ?, vote_date = ?, question = ?, result = ?, 
                            chamber = ?, description = ?, last_updated = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP 
                        WHERE vote_id = ?
                        """,
                        (vote.get("bill_id"), vote.get("bill_title"), vote.get("vote_date"), 
                         vote.get("question"), vote.get("result"), vote.get("chamber"), 
                         vote.get("description"), vote_id)
                    )
                    updated_count += 1
                else:
                    # Insert new record
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO votes 
                        (vote_id, bill_id, bill_title, vote_date, question, result, chamber, description) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (vote_id, vote.get("bill_id"), vote.get("bill_title"), vote.get("vote_date"), 
                         vote.get("question"), vote.get("result"), vote.get("chamber"), 
                         vote.get("description"))
                    )
                    new_count += 1
            
            except Exception as e:
                logger.error(f"Error syncing vote {vote.get('vote_id')}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Votes sync completed: {new_count} new, {updated_count} updated")
        return {"new": new_count, "updated": updated_count}
    
    async def sync_all(self, force=False):
        """Synchronize all data from Congress API to database.
        
        Args:
            force (bool): If True, update all records even if they exist
            
        Returns:
            dict: Results of all sync operations
        """
        logger.info(f"Starting full sync (force={force})")
        
        # Run all sync operations
        rep_result = await self.sync_representatives(force)
        bills_result = await self.sync_bills(force)
        votes_result = await self.sync_votes(force)
        
        return {
            "representatives": rep_result,
            "bills": bills_result,
            "votes": votes_result
        }
    
    def get_sync_status(self):
        """Get the current sync status (record counts and last updates).
        
        Returns:
            dict: Sync status information
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get record counts
        rep_count = cursor.execute("SELECT COUNT(*) as count FROM representatives").fetchone()['count']
        bill_count = cursor.execute("SELECT COUNT(*) as count FROM bills").fetchone()['count']
        vote_count = cursor.execute("SELECT COUNT(*) as count FROM votes").fetchone()['count']
        
        # Get latest update times
        rep_latest = cursor.execute("SELECT MAX(updated_at) as latest FROM representatives").fetchone()['latest']
        bill_latest = cursor.execute("SELECT MAX(updated_at) as latest FROM bills").fetchone()['latest']
        vote_latest = cursor.execute("SELECT MAX(updated_at) as latest FROM votes").fetchone()['latest']
        
        # Check API configuration
        api_config = cursor.execute("SELECT * FROM api_config LIMIT 1").fetchone()
        api_configured = api_config is not None and api_config['api_key'] is not None
        
        conn.close()
        
        return {
            "record_counts": {
                "representatives": rep_count,
                "bills": bill_count,
                "votes": vote_count
            },
            "latest_updates": {
                "representatives": rep_latest,
                "bills": bill_latest,
                "votes": vote_latest
            },
            "api_configured": api_configured
        }

# Get a singleton instance
sync_manager = SyncManager() 