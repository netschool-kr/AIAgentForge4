#AIAgentForge/AIAgentForge/state/dashboard_state.py:
import reflex as rx
from .base import BaseState
class DashboardState(BaseState):
    #... (users 리스트와 add_user 메서드는 동일)
    users: list[dict] = [
        {"name": "존 도", "age": 30, "role": "개발자"},
        {"name": "제인 도", "age": 28, "role": "디자이너"},
    ]
    def add_user(self, form_data: dict):
        if not form_data.get("name") or not form_data.get("age"):
            return rx.window_alert("이름과 나이는 비워둘 수 없습니다!")
        self.users.append(
            {
                "name": form_data["name"],
                "age": int(form_data["age"]),
                "role": "신규 사용자",
            }
        )
    @rx.var
    def total_users(self) -> int:
        """사용자 리스트의 길이를 반환하는 계산 변수."""
        return len(self.users)
