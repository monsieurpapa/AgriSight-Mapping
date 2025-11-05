import reflex as rx
from typing import TypedDict, Literal
import json
from app.states.map_state import MapState, Field
from reflex_enterprise.components.map.types import LatLng


class TimelineEvent(TypedDict):
    field_id: str
    date: str
    stage: Literal["Harvest", "Drying/Fermentation", "Processing", "Export"]
    description: str
    location: str


class SupplyChainStep(TypedDict):
    stage: str
    status: Literal["Completed", "In-Progress", "Pending"]
    details: str


class TraceabilityState(rx.State):
    """Manages traceability data, including timelines and supply chains."""

    timeline_events: list[TimelineEvent] = [
        {
            "field_id": "field-kivu-001",
            "date": "2023-06-10",
            "stage": "Harvest",
            "description": "Arabica coffee cherries harvested by hand.",
            "location": "Amani Dufatanye's Farm, South Kivu",
        },
        {
            "field_id": "field-kivu-001",
            "date": "2023-06-12",
            "stage": "Drying/Fermentation",
            "description": "Coffee cherries washed and laid out on drying beds.",
            "location": "Bukavu Washing Station",
        },
        {
            "field_id": "field-kivu-001",
            "date": "2023-07-01",
            "stage": "Processing",
            "description": "Dried beans milled and sorted for quality.",
            "location": "COOPEC-Kivu Plant, Bukavu",
        },
        {
            "field_id": "field-kivu-001",
            "date": "2023-07-15",
            "stage": "Export",
            "description": "Coffee bags shipped from Port of Matadi.",
            "location": "Port of Matadi",
        },
        {
            "field_id": "field-equateur-001",
            "date": "2023-09-25",
            "stage": "Harvest",
            "description": "Cocoa pods harvested from trees.",
            "location": "Lokole Bofunda's Farm, Équateur",
        },
        {
            "field_id": "field-equateur-001",
            "date": "2023-09-28",
            "stage": "Drying/Fermentation",
            "description": "Cocoa beans fermented in heaps and sun-dried.",
            "location": "Mbandaka Fermentation Center",
        },
    ]

    @rx.var
    async def selected_field_timeline(self) -> list[TimelineEvent]:
        """Get the timeline events for the currently selected field."""
        map_state = await self.get_state(MapState)
        if not map_state.selected_field_id:
            return []
        return sorted(
            [
                event
                for event in self.timeline_events
                if event["field_id"] == map_state.selected_field_id
            ],
            key=lambda e: e["date"],
            reverse=True,
        )

    @rx.var
    async def supply_chain_data(self) -> list[SupplyChainStep]:
        """Get a mock supply chain status for the selected field."""
        map_state = await self.get_state(MapState)
        if not map_state.selected_field_id:
            return []
        timeline = await self.selected_field_timeline
        stages_completed = {event["stage"] for event in timeline}
        chain = []
        all_stages = ["Harvest", "Processing", "Distribution", "Retail"]
        for stage in all_stages:
            if stage in stages_completed:
                status = "Completed"
                details = f"{stage} step finished."
            else:
                status = "Pending"
                details = f"Awaiting {stage}."
            chain.append({"stage": stage, "status": status, "details": details})
        return chain

    def _serialize_latlng(self, latlng: LatLng) -> dict:
        return {"lat": latlng.lat, "lng": latlng.lng}

    @rx.event
    async def export_fields_csv(self) -> rx.event.EventSpec:
        """Export field data to a CSV file."""
        map_state = await self.get_state(MapState)
        fields = await map_state.permissioned_fields
        header = """id,farmer_id,farmer_name,crop,area
"""
        csv_data = (
            header
            + """
""".join(
                (
                    f"{f['id']},{f['farmer_id']},{f['farmer_name']},{f['crop']},{f['area']}"
                    for f in fields
                )
            )
        )
        return rx.download(data=csv_data, filename="agritrace_fields.csv")

    @rx.event
    async def export_fields_json(self) -> rx.event.EventSpec:
        """Export field data to a JSON file."""
        map_state = await self.get_state(MapState)
        fields = await map_state.permissioned_fields
        serializable_fields = []
        for f in fields:
            field_copy = f.copy()
            field_copy["polygon"] = [self._serialize_latlng(p) for p in f["polygon"]]
            serializable_fields.append(field_copy)
        json_data = json.dumps({"fields": serializable_fields}, indent=2)
        return rx.download(data=json_data, filename="agritrace_fields.json")