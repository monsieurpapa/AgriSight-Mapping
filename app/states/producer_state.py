import reflex as rx
from app.states.map_state import MapState, Field, Farmer, Cooperative
from app.states.traceability_state import TraceabilityState, TimelineEvent
from typing import TypedDict, Literal


class ProducerState(rx.State):
    """Manages the state for the detailed producer view page."""

    current_producer_id: str = ""
    producer: Farmer | None = None
    cooperative: Cooperative | None = None
    producer_fields: list[Field] = []

    @rx.var
    def producer_avatar_url(self) -> str:
        if self.producer:
            return f"https://api.dicebear.com/9.x/notionists/svg?seed={self.producer['name']}"
        return ""

    @rx.var
    def cooperative_name(self) -> str:
        return self.cooperative["name"] if self.cooperative else "N/A"

    @rx.var
    def total_area(self) -> float:
        return round(sum((f["area"] for f in self.producer_fields)), 2)

    @rx.var
    def total_fields(self) -> int:
        return len(self.producer_fields)

    @rx.var
    def average_yield(self) -> float:
        if not self.producer_fields:
            return 0.0
        base_yield = 1.2
        variation = abs(hash(self.current_producer_id)) % 10 / 10.0
        return round(base_yield + variation * 1.8, 2)

    @rx.event
    async def load_producer_data(self):
        """Load all data related to the producer based on the URL parameter."""
        self.current_producer_id = self.router.page.params.get("producer_id", "")
        if not self.current_producer_id:
            return
        map_state = await self.get_state(MapState)
        for p in map_state.farmers:
            if p["id"] == self.current_producer_id:
                self.producer = p
                break
        if self.producer is None:
            return
        for c in map_state.cooperatives:
            if c["id"] == self.producer["cooperative_id"]:
                self.cooperative = c
                break
        self.producer_fields = [
            f for f in map_state.fields if f["farmer_id"] == self.current_producer_id
        ]