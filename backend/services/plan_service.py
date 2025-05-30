# Placeholder for plan-related service functions
# e.g., get_plan, get_plans, create_plan

from sqlmodel import Session, select
from typing import List, Optional

from ..models.plan import Plan, PlanCreate, PlanUpdate

def get_plan(db: Session, plan_id: int) -> Optional[Plan]:
    return db.get(Plan, plan_id)

def get_plan_by_name(db: Session, name: str) -> Optional[Plan]:
    statement = select(Plan).where(Plan.name == name)
    plan = db.exec(statement).first()
    return plan

def get_plans(db: Session, skip: int = 0, limit: int = 100) -> List[Plan]:
    statement = select(Plan).offset(skip).limit(limit)
    plans = db.exec(statement).all()
    return plans

def create_plan(db: Session, plan: PlanCreate) -> Plan:
    db_plan = Plan.model_validate(plan)
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def update_plan(db: Session, db_plan: Plan, plan_in: PlanUpdate) -> Plan:
    plan_data = plan_in.model_dump(exclude_unset=True)
    for key, value in plan_data.items():
        setattr(db_plan, key, value)
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def delete_plan(db: Session, db_plan: Plan):
    db.delete(db_plan)
    db.commit()
    return {"ok": True}

# Function to maybe create default plans on startup
def create_default_plans(db: Session):
    default_plans = [
        PlanCreate(name="Free", description="Basic plan with limited features", max_scheduled_campaigns=1),
        PlanCreate(name="Pro", description="Professional plan with AI training", allow_ai_training=True, max_scheduled_campaigns=10, allow_custom_branding=True),
        PlanCreate(name="Enterprise", description="Full features including API access", allow_ai_training=True, max_scheduled_campaigns=-1, allow_custom_branding=True, allow_api_access=True) # -1 for unlimited
    ]
    for plan_data in default_plans:
        existing_plan = get_plan_by_name(db, name=plan_data.name)
        if not existing_plan:
            create_plan(db, plan=plan_data)
            print(f"Created default plan: {plan_data.name}")

