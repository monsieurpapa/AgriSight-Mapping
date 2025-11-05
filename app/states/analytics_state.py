import reflex as rx
from typing import TypedDict
from app.states.traceability_state import TraceabilityState


class CropData(TypedDict):
    name: str
    value: int
    fill: str


CROP_COLORS = {
    "Coffee": "#6F4E37",
    "Cocoa": "#D2691E",
    "Arabica Coffee": "#8B4513",
    "Robusta Coffee": "#A0522D",
}


class AnalyticsState(rx.State):
    """The state for the analytics components."""

    crop_distribution: list[CropData] = []

    @rx.var
    async def yield_data(self) -> list[dict[str, int | str]]:
        """Get yield data based on the selected field's timeline."""
        trace_state = await self.get_state(TraceabilityState)
        timeline = await trace_state.selected_field_timeline
        if not timeline:
            return [
                {"year": 2020, "yield": 150},
                {"year": 2021, "yield": 175},
                {"year": 2022, "yield": 160},
                {"year": 2023, "yield": 180},
            ]
        field_id_hash = abs(hash(timeline[0]["field_id"])) % 100
        return [
            {"year": 2020, "yield": 150 + field_id_hash % 20 - 10},
            {"year": 2021, "yield": 175 + field_id_hash % 15 - 5},
            {"year": 2022, "yield": 160 + field_id_hash % 25 - 15},
            {"year": 2023, "yield": 180 + field_id_hash % 10},
        ]