"""
Action plan generation for team improvements.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class ActionItem:
    """A single action item in a plan."""
    title: str
    description: str
    owner: str
    deadline: datetime
    dependencies: List[str]
    status: str = "pending"  # pending, in_progress, completed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "owner": self.owner,
            "deadline": self.deadline.isoformat(),
            "dependencies": self.dependencies,
            "status": self.status,
        }


@dataclass
class ActionPlan:
    """Complete action plan."""
    goal: str
    items: List[ActionItem]
    timeline_weeks: int
    success_metrics: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "goal": self.goal,
            "items": [item.to_dict() for item in self.items],
            "timeline_weeks": self.timeline_weeks,
            "success_metrics": self.success_metrics,
        }


class ActionPlanGenerator:
    """
    Generates actionable plans from recommendations.
    """
    
    def generate_plan(
        self,
        goal: str,
        recommendations: List[Any],
        team_size: int = 5
    ) -> ActionPlan:
        """
        Generate action plan from recommendations.
        
        Args:
            goal: Overall goal
            recommendations: List of recommendations
            team_size: Size of team
            
        Returns:
            Complete action plan
        """
        items = []
        base_date = datetime.now()
        
        # Generate action items based on recommendations
        for i, rec in enumerate(recommendations[:3]):  # Top 3 recommendations
            item = ActionItem(
                title=f"Implement: {rec.title}",
                description=rec.description,
                owner="Team Lead",
                deadline=base_date + timedelta(weeks=(i + 1) * 2),
                dependencies=[]
            )
            items.append(item)
            
        # Add review item
        items.append(ActionItem(
            title="Review Progress",
            description="Assess implementation progress and adjust plan",
            owner="Team Lead",
            deadline=base_date + timedelta(weeks=8),
            dependencies=[item.title for item in items[:-1]]
        ))
        
        return ActionPlan(
            goal=goal,
            items=items,
            timeline_weeks=8,
            success_metrics=[
                "Improved team satisfaction scores",
                "Increased productivity metrics",
                "Better communication ratings"
            ]
        )
        
    def track_progress(
        self,
        plan: ActionPlan
    ) -> Dict[str, Any]:
        """
        Track progress on action plan.
        
        Args:
            plan: Action plan to track
            
        Returns:
            Progress metrics
        """
        total_items = len(plan.items)
        completed = sum(1 for item in plan.items if item.status == "completed")
        in_progress = sum(1 for item in plan.items if item.status == "in_progress")
        
        return {
            "total_items": total_items,
            "completed": completed,
            "in_progress": in_progress,
            "pending": total_items - completed - in_progress,
            "completion_percentage": (completed / total_items * 100) if total_items > 0 else 0,
        }
