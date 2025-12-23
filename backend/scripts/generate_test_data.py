from sqlalchemy.orm import Session
from backend.database.session import SessionLocal, Base, engine
from backend.database.models import Voter, Candidate
from backend.database.crud import add_candidate, add_voter


# CONFIG

NUM_VOTERS = 20
CANDIDATE_NAMES = [
    "Alice Johnson",
    "Bob Singh",
    "Charlie Mehra"
]


# MAIN

def clear_old_data(db: Session):
    db.query(Voter).delete()
    db.query(Candidate).delete()
    db.commit()
    print("[*] Old data cleared.")


def generate_voters(db: Session):
    print(f"[*] Generating {NUM_VOTERS} voters...")

    for i in range(1, NUM_VOTERS + 1):
        voter_id = f"VOTER{i:03d}"         # e.g. VOTER001, VOTER002...
        add_voter(db, voter_id)

    print("[+] Voters generated.")


def generate_candidates(db: Session):
    print(f"[*] Adding {len(CANDIDATE_NAMES)} candidates...")

    for name in CANDIDATE_NAMES:
        add_candidate(db, name)

    print("[+] Candidates created.")


def main():
    print("=== VoteChain Test Data Generator ===")
    print("Creating tables if not present...")

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    clear_old = input("Clear old data? (y/n): ").strip().lower()
    if clear_old == "y":
        clear_old_data(db)

    generate_voters(db)
    generate_candidates(db)

    db.close()
    print("\nDone.")
    print("You now have sample voters and candidates in your database.")


if __name__ == "__main__":
    main()
