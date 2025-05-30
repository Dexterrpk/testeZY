#!/usr/bin/env python3
import sys
import os
# Add backend path to sys.path if running from ZYNAPSE root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.core.database import get_session, engine, SQLModel
from backend.models.user import UserCreate
from backend.services import user_service
from backend.services import plan_service # Import plan_service to create default plans

def main():
    print("Ensuring database and tables exist...")
    SQLModel.metadata.create_all(engine)

    print("Attempting to create default plans and superuser...")
    # Use context manager for session
    with next(get_session()) as session:
        # Create default plans first
        print("Checking/Creating default plans...")
        plan_service.create_default_plans(session)
        print("Default plans checked/created.")

        # Define superuser details
        email = "cleitonneri04@gmail.com"
        password = "dexter" # Use a simple password for testing, remind user to change

        # Check if user already exists
        user = user_service.get_user_by_email(session, email=email)
        if not user:
            print(f"Creating superuser {email}...")
            # Assign a default plan (e.g., Enterprise) if needed, or let user service handle it
            # Fetch the Enterprise plan to assign its ID
            enterprise_plan = plan_service.get_plan_by_name(session, name="Enterprise")
            plan_id = enterprise_plan.id if enterprise_plan else None
            if not plan_id:
                print("Warning: Enterprise plan not found. Superuser might lack plan features.")

            user_in = UserCreate(
                email=email,
                password=password,
                full_name="Admin User",
                is_superuser=True,
                is_active=True,
                plan_id=plan_id # Assign Enterprise plan ID
            )
            user_service.create_user(db=session, user=user_in)
            print(f"Superuser '{email}' created successfully with password '{password}'. Please change it!")
        else:
            print(f"User '{email}' already exists.")

if __name__ == "__main__":
    main()

