"""
Congress API Module

This module provides functionality to interact with the Congress.gov API.
It handles fetching data about representatives, bills, and votes.
"""
import httpx
import logging
import os
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import ApiConfig, Representative, Bill, Vote

# Import configuration
from config import CONGRESS_API_KEY, CONGRESS_API_URL, is_api_configured

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CongressAPI:
    """Class to interact with the Congress API."""
    
    def __init__(self, db: Session):
        """Initialize the Congress API client."""
        self.db = db
        self.config = self._get_api_config()
        self.client = httpx.AsyncClient(
            base_url=self.config.get("base_url", CONGRESS_API_URL),
            timeout=30.0,
        )
        
    def _get_api_config(self) -> Dict[str, str]:
        """Get API configuration from the database or environment variables."""
        # Try to get config from database
        api_config = self.db.query(ApiConfig).filter(
            ApiConfig.name == "congress_api",
            ApiConfig.is_active == True
        ).first()
        
        if api_config:
            return {
                "api_key": api_config.api_key,
                "base_url": api_config.base_url or CONGRESS_API_URL
            }
        
        # Fall back to environment variables
        return {
            "api_key": CONGRESS_API_KEY,
            "base_url": CONGRESS_API_URL
        }
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the Congress API.
        
        Args:
            endpoint (str): API endpoint to request
            params (Dict[str, Any], optional): Query parameters
            
        Returns:
            Dict[str, Any]: API response data
        """
        if params is None:
            params = {}
            
        # Add API key to params
        params["api_key"] = self.config.get("api_key", "")
        
        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return {"error": str(e)}
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"error": str(e)}
    
    async def get_house_members(self) -> List[Dict[str, Any]]:
        """
        Get current House of Representatives members.
        
        Returns:
            List[Dict[str, Any]]: List of House members
        """
        logger.info("Fetching House members from Congress API")
        
        # Get current congress number
        congress = 118  # This should be determined dynamically in a real app
        
        try:
            # The actual endpoint is /congress/{congress}/members with chamber filter
            response = await self._make_request(f"/congress/{congress}/members", params={
                "chamber": "house",
                "format": "json"
            })
            
            if "error" in response:
                logger.error(f"Error fetching House members: {response['error']}")
                return []
                
            # Extract and normalize members data
            members = response.get("members", [])
            
            # Transform data to our format
            normalized_members = []
            for member in members:
                normalized_members.append({
                    "id": member.get("bioguideId", ""),
                    "name": f"{member.get('firstName', '')} {member.get('lastName', '')}",
                    "state": member.get("state", ""),
                    "district": member.get("district", ""),
                    "party": member.get("party", ""),
                    "chamber": "House"
                })
                
            return normalized_members
            
        except Exception as e:
            logger.error(f"Error processing House members data: {str(e)}")
            return []
    
    async def get_senate_members(self) -> List[Dict[str, Any]]:
        """
        Get current Senate members.
        
        Returns:
            List[Dict[str, Any]]: List of Senate members
        """
        logger.info("Fetching Senate members from Congress API")
        
        # Get current congress number
        congress = 118  # This should be determined dynamically in a real app
        
        try:
            # The actual endpoint is /congress/{congress}/members with chamber filter
            response = await self._make_request(f"/congress/{congress}/members", params={
                "chamber": "senate",
                "format": "json"
            })
            
            if "error" in response:
                logger.error(f"Error fetching Senate members: {response['error']}")
                return []
                
            # Extract and normalize members data
            members = response.get("members", [])
            
            # Transform data to our format
            normalized_members = []
            for member in members:
                normalized_members.append({
                    "id": member.get("bioguideId", ""),
                    "name": f"{member.get('firstName', '')} {member.get('lastName', '')}",
                    "state": member.get("state", ""),
                    "district": "",  # Senators don't have districts
                    "party": member.get("party", ""),
                    "chamber": "Senate"
                })
                
            return normalized_members
            
        except Exception as e:
            logger.error(f"Error processing Senate members data: {str(e)}")
            return []
    
    async def get_member_details(self, member_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific member of Congress.
        
        Args:
            member_id (str): Bioguide ID of the member
            
        Returns:
            Dict[str, Any]: Member details
        """
        logger.info(f"Fetching details for member {member_id}")
        
        try:
            response = await self._make_request(f"/member/{member_id}")
            
            if "error" in response:
                logger.error(f"Error fetching member details: {response['error']}")
                return {}
                
            # Extract and normalize member data
            member_data = response.get("member", {})
            
            # Transform data to our format
            normalized_data = {
                "id": member_id,
                "name": f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}",
                "state": member_data.get("state", ""),
                "district": member_data.get("district", ""),
                "party": member_data.get("party", ""),
                "chamber": member_data.get("chamber", ""),
                "terms": member_data.get("terms", []),
                "committees": member_data.get("committees", []),
                "url": member_data.get("url", ""),
                "twitter": member_data.get("twitterAccount", ""),
                "facebook": member_data.get("facebookAccount", ""),
                "youtube": member_data.get("youtubeAccount", "")
            }
                
            return normalized_data
            
        except Exception as e:
            logger.error(f"Error processing member details: {str(e)}")
            return {}
    
    async def get_recent_bills(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent bills from Congress.
        
        Args:
            limit (int): Maximum number of bills to return
            
        Returns:
            List[Dict[str, Any]]: List of recent bills
        """
        logger.info(f"Fetching recent bills (limit: {limit})")
        
        try:
            # Use the ISO 8601 format for date parameters (YYYY-MM-DDTHH:MM:SSZ)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00Z")
            
            response = await self._make_request("/bill", params={
                "limit": limit,
                "sort": "updateDate",
                "fromDateTime": thirty_days_ago,
                "format": "json"
            })
            
            if "error" in response:
                logger.error(f"Error fetching recent bills: {response['error']}")
                return []
                
            # Extract and normalize bills data
            bills = response.get("bills", [])
            
            # Transform data to our format
            normalized_bills = []
            for bill in bills:
                normalized_bills.append({
                    "bill_id": bill.get("billId", ""),
                    "title": bill.get("title", ""),
                    "introduced_date": bill.get("introducedDate", ""),
                    "status": bill.get("latestAction", {}).get("text", ""),
                    "url": bill.get("url", ""),
                    "sponsor": bill.get("sponsor", {}).get("name", "")
                })
                
            return normalized_bills
            
        except Exception as e:
            logger.error(f"Error processing recent bills data: {str(e)}")
            return []
    
    async def get_bill_details(self, bill_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific bill.
        
        Args:
            bill_id (str): ID of the bill
            
        Returns:
            Dict[str, Any]: Bill details
        """
        logger.info(f"Fetching details for bill {bill_id}")
        
        try:
            # Parse bill ID to extract congress, bill type, and bill number
            # Format: 118hr1 (118th Congress, House Resolution 1)
            parts = bill_id.split('hr')
            if len(parts) != 2:
                logger.error(f"Invalid bill ID format: {bill_id}")
                return {}
                
            congress = parts[0]
            bill_number = parts[1]
            bill_type = "hr"  # This is simplified, should handle different bill types
            
            response = await self._make_request(
                f"/bill/{congress}/{bill_type}/{bill_number}"
            )
            
            if "error" in response:
                logger.error(f"Error fetching bill details: {response['error']}")
                return {}
                
            # Extract and normalize bill data
            bill_data = response.get("bill", {})
            
            # Transform data to our format
            normalized_data = {
                "bill_id": bill_id,
                "title": bill_data.get("title", ""),
                "introduced_date": bill_data.get("introducedDate", ""),
                "status": bill_data.get("latestAction", {}).get("text", ""),
                "url": bill_data.get("url", ""),
                "sponsor": bill_data.get("sponsor", {}).get("name", ""),
                "cosponsors": bill_data.get("cosponsors", []),
                "summary": bill_data.get("summary", ""),
                "actions": bill_data.get("actions", []),
                "votes": bill_data.get("votes", [])
            }
                
            return normalized_data
            
        except Exception as e:
            logger.error(f"Error processing bill details: {str(e)}")
            return {}
    
    async def get_recent_votes(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent votes from Congress.
        
        Args:
            limit (int): Maximum number of votes to return
            
        Returns:
            List[Dict[str, Any]]: List of recent votes
        """
        logger.info(f"Fetching recent votes (limit: {limit})")
        
        try:
            # Use the ISO 8601 format for date parameters (YYYY-MM-DDTHH:MM:SSZ)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00Z")
            
            response = await self._make_request("/vote", params={
                "limit": limit,
                "sort": "updateDate",
                "fromDateTime": thirty_days_ago,
                "format": "json"
            })
            
            if "error" in response:
                logger.error(f"Error fetching recent votes: {response['error']}")
                return []
                
            # Extract and normalize votes data
            votes = response.get("votes", [])
            
            # Transform data to our format
            normalized_votes = []
            for vote in votes:
                normalized_votes.append({
                    "vote_id": vote.get("voteId", ""),
                    "bill_id": vote.get("billId", ""),
                    "bill_title": vote.get("title", ""),
                    "vote_date": vote.get("date", ""),
                    "question": vote.get("question", ""),
                    "result": vote.get("result", ""),
                    "chamber": vote.get("chamber", ""),
                    "description": vote.get("description", "")
                })
                
            return normalized_votes
            
        except Exception as e:
            logger.error(f"Error processing recent votes data: {str(e)}")
            return []
            
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Function to get a Congress API client
def get_congress_api(db: Session):
    """
    Get a Congress API client.
    
    Args:
        db (Session): Database session
        
    Returns:
        CongressAPI: Instance of the Congress API client
    """
    return CongressAPI(db)

# Helper functions for data synchronization

async def sync_representatives(db: Session, current_congress: int = 118):
    """
    Synchronize representatives data from the Congress API.
    
    Args:
        db: Database session
        current_congress: Current Congress number
    """
    api = CongressAPI(db)
    
    try:
        # Sync House members
        house_members = await api.search_members(congress=current_congress, chamber="house")
        _update_representatives(db, house_members, "House")
        
        # Sync Senate members
        senate_members = await api.search_members(congress=current_congress, chamber="senate")
        _update_representatives(db, senate_members, "Senate")
        
        logger.info(f"Successfully synchronized representatives for the {current_congress}th Congress")
    except Exception as e:
        logger.error(f"Error synchronizing representatives: {str(e)}")
    finally:
        await api.close()

def _update_representatives(db: Session, members: List[Dict[str, Any]], chamber: str):
    """
    Update representative records in the database from API data.
    
    Args:
        db: Database session
        members: List of member data from the API
        chamber: Chamber ('House' or 'Senate')
    """
    count_created = 0
    count_updated = 0
    
    for member_data in members:
        congress_id = member_data.get("memberId")
        if not congress_id:
            continue
        
        # Check if representative already exists
        rep = db.query(Representative).filter(Representative.congress_id == congress_id).first()
        
        if rep:
            # Update existing representative
            rep.name = f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}"
            rep.state = member_data.get("state", "")
            rep.district = member_data.get("district")
            rep.party = member_data.get("party", "")
            rep.chamber = chamber
            rep.website = member_data.get("officialWebsiteUrl", "")
            rep.last_updated = datetime.utcnow()
            count_updated += 1
        else:
            # Create new representative
            new_rep = Representative(
                name=f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}",
                state=member_data.get("state", ""),
                district=member_data.get("district"),
                party=member_data.get("party", ""),
                chamber=chamber,
                congress_id=congress_id,
                website=member_data.get("officialWebsiteUrl", ""),
                last_updated=datetime.utcnow()
            )
            db.add(new_rep)
            count_created += 1
    
    db.commit()
    logger.info(f"Representatives sync: {count_created} created, {count_updated} updated")

async def sync_recent_bills(db: Session, current_congress: int = 118, days_back: int = 30):
    """
    Synchronize recent bills data from the Congress API.
    
    Args:
        db: Database session
        current_congress: Current Congress number
        days_back: Number of days to look back for recent bills
    """
    api = CongressAPI(db)
    
    try:
        introduced_after = datetime.utcnow() - timedelta(days=days_back)
        
        # Sync recent bills
        bills = await api.search_bills(
            congress=current_congress,
            introduced_after=introduced_after
        )
        
        count_created = 0
        count_updated = 0
        
        for bill_data in bills:
            congress_id = bill_data.get("billId")
            if not congress_id:
                continue
            
            # Check if bill already exists
            bill = db.query(Bill).filter(Bill.congress_id == congress_id).first()
            
            # Parse dates
            introduced_date = None
            if bill_data.get("introducedDate"):
                introduced_date = datetime.strptime(bill_data.get("introducedDate"), "%Y-%m-%d")
            
            last_action_date = None
            if bill_data.get("latestAction", {}).get("actionDate"):
                last_action_date = datetime.strptime(bill_data.get("latestAction", {}).get("actionDate"), "%Y-%m-%d")
            
            title = bill_data.get("title", "")
            bill_number = bill_data.get("billNumber", "")
            bill_type = bill_data.get("billType", "")
            formatted_number = f"{bill_type.upper()} {bill_number}"
            
            if bill:
                # Update existing bill
                bill.title = title
                bill.bill_number = formatted_number
                bill.status = bill_data.get("latestAction", {}).get("text", "")
                bill.introduced_date = introduced_date
                bill.last_action_date = last_action_date
                bill.url = bill_data.get("url", "")
                bill.last_updated = datetime.utcnow()
                count_updated += 1
            else:
                # Create new bill
                new_bill = Bill(
                    bill_number=formatted_number,
                    title=title,
                    status=bill_data.get("latestAction", {}).get("text", ""),
                    introduced_date=introduced_date,
                    last_action_date=last_action_date,
                    congress_session=current_congress,
                    congress_id=congress_id,
                    url=bill_data.get("url", ""),
                    last_updated=datetime.utcnow()
                )
                db.add(new_bill)
                count_created += 1
        
        db.commit()
        logger.info(f"Bills sync: {count_created} created, {count_updated} updated")
        
    except Exception as e:
        logger.error(f"Error synchronizing bills: {str(e)}")
    finally:
        await api.close()

async def sync_member_votes(db: Session, rep_id: int, current_congress: int = 118):
    """
    Synchronize voting records for a specific representative.
    
    Args:
        db: Database session
        rep_id: Representative ID in the database
        current_congress: Current Congress number
    """
    # Get representative
    rep = db.query(Representative).filter(Representative.id == rep_id).first()
    if not rep or not rep.congress_id:
        logger.error(f"Cannot sync votes: Representative with ID {rep_id} not found or missing congress_id")
        return
    
    api = CongressAPI(db)
    
    try:
        # Get detailed member info with voting history
        member_data = await api.get_member(rep.congress_id)
        
        # Process votes
        votes_data = member_data.get("votes", [])
        _process_member_votes(db, rep, votes_data)
        
        logger.info(f"Successfully synchronized votes for representative {rep.name}")
    except Exception as e:
        logger.error(f"Error synchronizing votes for representative {rep.name}: {str(e)}")
    finally:
        await api.close()

def _process_member_votes(db: Session, rep: Representative, votes_data: List[Dict[str, Any]]):
    """
    Process and save voting records for a representative.
    
    Args:
        db: Database session
        rep: Representative object
        votes_data: List of vote data from the API
    """
    count_created = 0
    
    for vote_data in votes_data:
        congress_vote_id = vote_data.get("voteId")
        if not congress_vote_id:
            continue
        
        # Check if we already have this vote
        existing_vote = db.query(Vote).filter(
            Vote.representative_id == rep.id,
            Vote.congress_vote_id == congress_vote_id
        ).first()
        
        if existing_vote:
            continue
        
        # Get or create the bill
        bill_number = vote_data.get("billNumber")
        if not bill_number:
            continue
        
        bill = db.query(Bill).filter(Bill.bill_number == bill_number).first()
        if not bill:
            # Create a placeholder bill that can be updated later
            bill = Bill(
                bill_number=bill_number,
                title=vote_data.get("billTitle", f"Bill {bill_number}"),
                congress_session=vote_data.get("congress", 0),
                created_at=datetime.utcnow()
            )
            db.add(bill)
            db.flush()  # Get ID without committing
        
        # Parse vote date
        vote_date = None
        if vote_data.get("date"):
            try:
                vote_date = datetime.strptime(vote_data.get("date"), "%Y-%m-%d")
            except ValueError:
                vote_date = datetime.utcnow()
        else:
            vote_date = datetime.utcnow()
        
        # Create the vote record
        new_vote = Vote(
            representative_id=rep.id,
            bill_id=bill.id,
            vote_position=vote_data.get("position", "Unknown"),
            vote_date=vote_date,
            congress_vote_id=congress_vote_id
        )
        
        db.add(new_vote)
        count_created += 1
    
    db.commit()
    logger.info(f"Votes sync for {rep.name}: {count_created} created") 