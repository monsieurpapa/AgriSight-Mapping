import reflex as rx
from reflex_enterprise.components.map.types import LatLng, latlng
from typing import TypedDict, Literal
from app.states.auth_state import AuthState, Cooperative, Farmer


class Field(TypedDict):
    id: str
    farmer_id: str
    farmer_name: str
    crop: str
    area: float
    polygon: list[LatLng]


class PointOfInterest(TypedDict):
    id: str
    name: str
    type: Literal["Farm", "Warehouse", "Processing Plant"]
    location: LatLng


class MapState(rx.State):
    """The state for the map dashboard."""

    center: LatLng = latlng(lat=-4.3276, lng=15.3136)
    zoom: float = 6.0
    show_fields: bool = True
    show_pois: bool = True
    selected_field_id: str | None = None
    search_query: str = ""
    cooperatives: list[Cooperative] = [
        {"id": "coop-kivu", "name": "COOPEC-Kivu Coffee"},
        {"id": "coop-equateur", "name": "COCACO-DRC Cocoa"},
    ]
    farmers: list[Farmer] = [
        {"id": "farmer-001", "name": "Amani Dufatanye", "cooperative_id": "coop-kivu"},
        {"id": "farmer-002", "name": "Baraka Mwangaza", "cooperative_id": "coop-kivu"},
        {
            "id": "farmer-003",
            "name": "Lokole Bofunda",
            "cooperative_id": "coop-equateur",
        },
    ]
    fields: list[Field] = [
        {
            "id": "field-kivu-001",
            "farmer_id": "farmer-001",
            "farmer_name": "Amani Dufatanye",
            "crop": "Arabica Coffee",
            "area": 5.2,
            "polygon": [
                latlng(lat=-2.25, lng=28.85),
                latlng(lat=-2.26, lng=28.86),
                latlng(lat=-2.27, lng=28.85),
                latlng(lat=-2.26, lng=28.84),
            ],
        },
        {
            "id": "field-kivu-002",
            "farmer_id": "farmer-002",
            "farmer_name": "Baraka Mwangaza",
            "crop": "Robusta Coffee",
            "area": 7.8,
            "polygon": [
                latlng(lat=-2.94, lng=29.06),
                latlng(lat=-2.95, lng=29.07),
                latlng(lat=-2.96, lng=29.06),
                latlng(lat=-2.95, lng=29.05),
            ],
        },
        {
            "id": "field-equateur-001",
            "farmer_id": "farmer-003",
            "farmer_name": "Lokole Bofunda",
            "crop": "Cocoa",
            "area": 12.5,
            "polygon": [
                latlng(lat=0.05, lng=18.25),
                latlng(lat=0.06, lng=18.26),
                latlng(lat=0.05, lng=18.27),
                latlng(lat=0.04, lng=18.26),
            ],
        },
    ]
    points_of_interest: list[PointOfInterest] = [
        {
            "id": "poi-bukavu-warehouse",
            "name": "Bukavu Coffee Warehouse",
            "type": "Warehouse",
            "location": latlng(lat=-2.5044, lng=28.8611),
        },
        {
            "id": "poi-kisangani-plant",
            "name": "Kisangani Cocoa Processing",
            "type": "Processing Plant",
            "location": latlng(lat=0.515, lng=25.195),
        },
        {
            "id": "poi-goma-farm",
            "name": "Goma Farmstead",
            "type": "Farm",
            "location": latlng(lat=-1.675, lng=29.225),
        },
    ]

    @rx.event
    def toggle_fields(self, checked: bool):
        self.show_fields = checked

    @rx.event
    def toggle_pois(self, checked: bool):
        self.show_pois = checked

    @rx.event
    def select_field(self, field_id: str):
        if self.selected_field_id == field_id:
            self.selected_field_id = None
        else:
            self.selected_field_id = field_id

    @rx.event
    def go_to_producer_page(self, farmer_id: str) -> rx.event.EventSpec:
        return rx.redirect(f"/producers/{farmer_id}")

    async def _update_crop_distribution(self):
        """Helper to update analytics state when fields change."""
        from app.states.analytics_state import AnalyticsState, CROP_COLORS

        analytics_state = await self.get_state(AnalyticsState)
        dist: dict[str, int] = {}
        for f in self.fields:
            dist[f["crop"]] = dist.get(f["crop"], 0) + 1
        analytics_state.crop_distribution = [
            {"name": crop, "value": count, "fill": CROP_COLORS.get(crop, "#9E9E9E")}
            for crop, count in dist.items()
        ]

    @rx.event
    async def add_field(self, field_data: Field):
        """Adds a new field to the state."""
        self.fields = [*self.fields, field_data]
        await self._update_crop_distribution()

    @rx.event
    async def update_field_data(self, field_data: Field):
        """Updates an existing field in the state."""
        self.fields = [
            field_data if f["id"] == field_data["id"] else f for f in self.fields
        ]
        await self._update_crop_distribution()

    @rx.event
    async def remove_field(self, field_id: str):
        """Removes a field from the state."""
        self.fields = [f for f in self.fields if f["id"] != field_id]
        await self._update_crop_distribution()

    @rx.event
    def add_poi(self, poi_data: PointOfInterest):
        """Adds a new POI to the state."""
        self.points_of_interest = [*self.points_of_interest, poi_data]

    @rx.event
    def update_poi_data(self, poi_data: PointOfInterest):
        """Updates an existing POI in the state."""
        self.points_of_interest = [
            poi_data if p["id"] == poi_data["id"] else p
            for p in self.points_of_interest
        ]

    @rx.event
    def remove_poi(self, poi_id: str):
        """Removes a POI from the state."""
        self.points_of_interest = [
            p for p in self.points_of_interest if p["id"] != poi_id
        ]

    @rx.var
    async def permissioned_fields(self) -> list[Field]:
        """Get fields based on the current user's role and partnerships."""
        auth_state = await self.get_state(AuthState)
        user = auth_state.current_user
        if user is None or user["role"] == "admin":
            return self.fields
        if user["role"] == "buyer":
            partner_coop_ids = user["partnerships"]
            partner_farmer_ids = {
                f["id"] for f in self.farmers if f["cooperative_id"] in partner_coop_ids
            }
            return [f for f in self.fields if f["farmer_id"] in partner_farmer_ids]
        if user["role"] == "cooperative":
            coop_id = user["cooperative_id"]
            farmer_ids_in_coop = {
                f["id"] for f in self.farmers if f["cooperative_id"] == coop_id
            }
            return [f for f in self.fields if f["farmer_id"] in farmer_ids_in_coop]
        return []

    @rx.var
    async def filtered_fields(self) -> list[Field]:
        """Get the fields filtered by the search query and permissions."""
        fields = await self.permissioned_fields
        if not self.search_query:
            return fields
        return [
            f
            for f in fields
            if self.search_query.lower() in f["farmer_name"].lower()
            or self.search_query.lower() in f["crop"].lower()
        ]

    @rx.var
    async def total_area(self) -> float:
        """Calculate the total area of all fields."""
        fields = await self.permissioned_fields
        return round(sum((f["area"] for f in fields)), 2)

    @rx.var
    async def total_fields(self) -> int:
        fields = await self.permissioned_fields
        return len(fields)