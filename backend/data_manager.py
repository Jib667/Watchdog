import csv
import json
import logging
import os
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import Representative, Bill, Vote, ApiConfig, engine, SessionLocal

# Import Congress API utilities
from congress_api import (
    CongressAPI,
    sync_representatives,
    sync_recent_bills,
    sync_member_votes
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_representatives_from_csv(csv_file_path):
    """
    Import representatives data from a CSV file
    
    Expected CSV format:
    name,state,district,party,chamber,bio,image_url,website,twitter,facebook
    """
    logger.info(f"Importing representatives from {csv_file_path}")
    
    if not os.path.exists(csv_file_path):
        logger.error(f"File not found: {csv_file_path}")
        return
    
    # Create database session
    db = SessionLocal()
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            count = 0
            
            for row in csv_reader:
                # Convert district to integer if present, otherwise None
                district = int(row.get('district')) if row.get('district') and row.get('district').isdigit() else None
                
                # Create new representative
                rep = Representative(
                    name=row.get('name'),
                    state=row.get('state'),
                    district=district,
                    party=row.get('party'),
                    chamber=row.get('chamber'),
                    bio=row.get('bio'),
                    image_url=row.get('image_url'),
                    website=row.get('website'),
                    twitter=row.get('twitter'),
                    facebook=row.get('facebook')
                )
                
                db.add(rep)
                count += 1
            
            db.commit()
            logger.info(f"Successfully imported {count} representatives")
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error importing representatives: {str(e)}")
    
    finally:
        db.close()

def import_bills_from_json(json_file_path):
    """
    Import bills data from a JSON file
    
    Expected JSON format:
    [
        {
            "bill_number": "H.R.1234",
            "title": "Bill Title",
            "description": "Bill Description",
            "status": "Introduced",
            "introduced_date": "2023-01-15",
            "last_action_date": "2023-02-20",
            "congress_session": 118
        },
        ...
    ]
    """
    logger.info(f"Importing bills from {json_file_path}")
    
    if not os.path.exists(json_file_path):
        logger.error(f"File not found: {json_file_path}")
        return
    
    # Create database session
    db = SessionLocal()
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            bills_data = json.load(f)
            count = 0
            
            for bill_data in bills_data:
                # Parse dates if present
                introduced_date = None
                if bill_data.get('introduced_date'):
                    try:
                        introduced_date = datetime.strptime(bill_data.get('introduced_date'), '%Y-%m-%d')
                    except ValueError:
                        logger.warning(f"Invalid introduced_date format for bill {bill_data.get('bill_number')}")
                
                last_action_date = None
                if bill_data.get('last_action_date'):
                    try:
                        last_action_date = datetime.strptime(bill_data.get('last_action_date'), '%Y-%m-%d')
                    except ValueError:
                        logger.warning(f"Invalid last_action_date format for bill {bill_data.get('bill_number')}")
                
                # Create new bill
                bill = Bill(
                    bill_number=bill_data.get('bill_number'),
                    title=bill_data.get('title'),
                    description=bill_data.get('description'),
                    status=bill_data.get('status'),
                    introduced_date=introduced_date,
                    last_action_date=last_action_date,
                    congress_session=bill_data.get('congress_session')
                )
                
                db.add(bill)
                count += 1
            
            db.commit()
            logger.info(f"Successfully imported {count} bills")
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error importing bills: {str(e)}")
    
    finally:
        db.close()

def import_votes_from_csv(csv_file_path):
    """
    Import votes data from a CSV file
    
    Expected CSV format:
    representative_id,bill_id,vote_position,vote_date
    """
    logger.info(f"Importing votes from {csv_file_path}")
    
    if not os.path.exists(csv_file_path):
        logger.error(f"File not found: {csv_file_path}")
        return
    
    # Create database session
    db = SessionLocal()
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            count = 0
            
            for row in csv_reader:
                # Parse vote date
                vote_date = None
                if row.get('vote_date'):
                    try:
                        vote_date = datetime.strptime(row.get('vote_date'), '%Y-%m-%d')
                    except ValueError:
                        logger.warning(f"Invalid vote_date format for representative {row.get('representative_id')} on bill {row.get('bill_id')}")
                        continue
                
                # Skip if vote_date is missing
                if not vote_date:
                    logger.warning(f"Skipping vote due to missing vote_date for representative {row.get('representative_id')} on bill {row.get('bill_id')}")
                    continue
                
                # Create new vote
                vote = Vote(
                    representative_id=int(row.get('representative_id')),
                    bill_id=int(row.get('bill_id')),
                    vote_position=row.get('vote_position'),
                    vote_date=vote_date
                )
                
                db.add(vote)
                count += 1
            
            db.commit()
            logger.info(f"Successfully imported {count} votes")
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error importing votes: {str(e)}")
    
    finally:
        db.close()

def generate_sample_data(num_reps=10, num_bills=5, num_votes=20):
    """Generate sample data for development and testing"""
    logger.info("Generating sample data for development")
    
    # Create database session
    db = SessionLocal()
    try:
        # Sample representatives
        chambers = ['House', 'Senate']
        parties = ['Republican', 'Democratic', 'Independent']
        states = ['CA', 'TX', 'NY', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
        
        for i in range(1, num_reps + 1):
            chamber = chambers[i % 2]
            party = parties[i % 3]
            state = states[i % 10]
            district = i if chamber == 'House' else None
            
            rep = Representative(
                name=f"Representative {i}",
                state=state,
                district=district,
                party=party,
                chamber=chamber,
                bio=f"Biography for Representative {i}",
                image_url=f"https://example.com/images/rep{i}.jpg",
                website=f"https://www.rep{i}.gov",
                twitter=f"@rep{i}",
                facebook=f"rep{i}"
            )
            
            db.add(rep)
        
        db.commit()
        logger.info(f"Added {num_reps} sample representatives")
        
        # Sample bills
        statuses = ['Introduced', 'Passed House', 'Passed Senate', 'Signed into Law', 'Vetoed']
        
        for i in range(1, num_bills + 1):
            status = statuses[i % 5]
            introduced_date = datetime(2023, i, 15)
            last_action_date = datetime(2023, i + 1, 20) if i < 12 else None
            
            bill = Bill(
                bill_number=f"H.R.{1000 + i}",
                title=f"Sample Bill {i}",
                description=f"This is a sample bill description for bill {i}",
                status=status,
                introduced_date=introduced_date,
                last_action_date=last_action_date,
                congress_session=118
            )
            
            db.add(bill)
        
        db.commit()
        logger.info(f"Added {num_bills} sample bills")
        
        # Sample votes
        positions = ['Yes', 'No', 'Present', 'Not Voting']
        
        for i in range(1, num_votes + 1):
            rep_id = (i % num_reps) + 1
            bill_id = (i % num_bills) + 1
            position = positions[i % 4]
            vote_date = datetime(2023, (i % 12) + 1, (i % 28) + 1)
            
            vote = Vote(
                representative_id=rep_id,
                bill_id=bill_id,
                vote_position=position,
                vote_date=vote_date
            )
            
            db.add(vote)
        
        db.commit()
        logger.info(f"Added {num_votes} sample votes")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating sample data: {str(e)}")
    
    finally:
        db.close()

def reset_database():
    """Reset the database by dropping and recreating all tables"""
    logger.warning("Resetting database - all data will be lost!")
    
    from database import Base
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped")
    
    # Recreate all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Tables recreated")

# Congress API utilities

def setup_api_config(api_key, base_url=None):
    """
    Set up or update the Congress API configuration.
    
    Args:
        api_key: API key for the Congress API
        base_url: Base URL for the API (optional)
    """
    logger.info("Setting up Congress API configuration")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if config already exists
        config = db.query(ApiConfig).filter(ApiConfig.name == "congress_api").first()
        
        if config:
            # Update existing config
            config.api_key = api_key
            if base_url:
                config.base_url = base_url
            config.is_active = True
            config.updated_at = datetime.utcnow()
            logger.info("Updated existing Congress API configuration")
        else:
            # Create new config
            new_config = ApiConfig(
                name="congress_api",
                api_key=api_key,
                base_url=base_url or "https://api.congress.gov/v3",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(new_config)
            logger.info("Created new Congress API configuration")
        
        db.commit()
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error setting up API configuration: {str(e)}")
    
    finally:
        db.close()

async def test_api_connection():
    """
    Test the connection to the Congress API.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    logger.info("Testing Congress API connection")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create API client
        api = CongressAPI(db)
        
        # Try to get the current Congress
        response = await api._make_request("/congress", {"limit": 1})
        
        # Close client
        await api.close()
        
        logger.info("Successfully connected to Congress API")
        return True
    
    except Exception as e:
        logger.error(f"Error connecting to Congress API: {str(e)}")
        return False
    
    finally:
        db.close()

async def sync_congressional_data(days_back=30, current_congress=118):
    """
    Synchronize data from the Congress API including representatives and recent bills.
    
    Args:
        days_back: Number of days to look back for bills
        current_congress: Current Congress number
    """
    logger.info(f"Starting data synchronization from Congress API (looking back {days_back} days)")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Test connection first
        if not await test_api_connection():
            logger.error("Cannot proceed with synchronization due to API connection issues")
            return False
        
        # Sync representatives
        logger.info("Synchronizing representatives...")
        await sync_representatives(db, current_congress=current_congress)
        
        # Sync recent bills
        logger.info(f"Synchronizing bills from the last {days_back} days...")
        await sync_recent_bills(db, current_congress=current_congress, days_back=days_back)
        
        # Sync votes for all representatives
        reps = db.query(Representative).all()
        logger.info(f"Synchronizing votes for {len(reps)} representatives...")
        
        for rep in reps:
            if rep.id:
                logger.info(f"Synchronizing votes for {rep.name} (ID: {rep.id})...")
                await sync_member_votes(db, rep.id, current_congress=current_congress)
        
        logger.info("Data synchronization completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error during data synchronization: {str(e)}")
        return False
    
    finally:
        db.close()

def run_sync():
    """Run the sync process (helper function for command line use)"""
    asyncio.run(sync_congressional_data())

if __name__ == "__main__":
    # Check for command line arguments
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "reset":
            reset_database()
        
        elif command == "sample":
            generate_sample_data()
        
        elif command == "sync":
            # Get days_back from args if provided
            days_back = 30
            if len(sys.argv) > 2:
                try:
                    days_back = int(sys.argv[2])
                except ValueError:
                    pass
            
            # Run sync
            run_sync()
        
        else:
            print(f"Unknown command: {command}")
            print("Available commands: reset, sample, sync")
    
    else:
        # Default behavior - generate sample data
        generate_sample_data() 