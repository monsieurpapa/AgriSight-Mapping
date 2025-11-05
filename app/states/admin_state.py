import reflex as rx
import json
import logging
import time
import uuid
from app.states.map_state import (
    MapState,
    Farmer,
    Field,
    latlng,
    Cooperative,
    PointOfInterest,
)
from app.states.auth_state import AuthState


class AdminState(rx.State):
    """State for the admin dashboard, including GeoJSON import and CRUD operations."""

    is_uploading: bool = False
    import_summary: dict | None = None
    coop_dialog_open: bool = False
    farmer_dialog_open: bool = False
    field_dialog_open: bool = False
    poi_dialog_open: bool = False
    delete_dialog_open: bool = False
    editing_id: str | None = None
    form_coop_name: str = ""
    form_farmer_name: str = ""
    form_farmer_coop_id: str = ""
    form_field_farmer_id: str = ""
    form_field_crop: str = ""
    form_field_area: str = ""
    form_field_polygon: str = ""
    form_poi_name: str = ""
    form_poi_type: str = "Warehouse"
    form_poi_lat: str = ""
    form_poi_lng: str = ""
    item_to_delete: dict[str, str] | None = None

    @rx.event
    async def on_load(self):
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_admin:
            return rx.redirect("/")

    @rx.event
    def open_coop_dialog(self):
        self.coop_dialog_open = True

    @rx.event
    def close_coop_dialog(self):
        self.coop_dialog_open = False
        self.reset_coop_form()

    @rx.event
    def reset_coop_form(self):
        self.editing_id = None
        self.form_coop_name = ""

    @rx.event
    async def create_cooperative(self):
        map_state = await self.get_state(MapState)
        new_coop: Cooperative = {
            "id": f"coop-{uuid.uuid4().hex[:6]}",
            "name": self.form_coop_name,
        }
        map_state.cooperatives = [*map_state.cooperatives, new_coop]
        self.close_coop_dialog()

    @rx.event
    async def update_cooperative(self):
        map_state = await self.get_state(MapState)
        if self.editing_id:
            for i, coop in enumerate(map_state.cooperatives):
                if coop["id"] == self.editing_id:
                    map_state.cooperatives[i]["name"] = self.form_coop_name
                    break
            self.editing_id = None
        self.close_coop_dialog()

    @rx.event
    async def save_cooperative(self, form_data: dict):
        if self.editing_id:
            return await AdminState.update_cooperative()
        return await AdminState.create_cooperative()

    @rx.event
    def edit_cooperative(self, coop: Cooperative):
        self.editing_id = coop["id"]
        self.form_coop_name = coop["name"]
        self.open_coop_dialog()

    @rx.event
    async def delete_cooperative(self, coop_id: str):
        map_state = await self.get_state(MapState)
        map_state.cooperatives = [
            c for c in map_state.cooperatives if c["id"] != coop_id
        ]

    @rx.event
    def open_farmer_dialog(self):
        self.farmer_dialog_open = True

    @rx.event
    def close_farmer_dialog(self):
        self.farmer_dialog_open = False
        self.reset_farmer_form()

    @rx.event
    def reset_farmer_form(self):
        self.editing_id = None
        self.form_farmer_name = ""
        self.form_farmer_coop_id = ""

    @rx.event
    async def create_farmer(self):
        map_state = await self.get_state(MapState)
        new_farmer: Farmer = {
            "id": f"farmer-{uuid.uuid4().hex[:6]}",
            "name": self.form_farmer_name,
            "cooperative_id": self.form_farmer_coop_id,
        }
        map_state.farmers = [*map_state.farmers, new_farmer]
        self.close_farmer_dialog()

    @rx.event
    async def update_farmer(self):
        map_state = await self.get_state(MapState)
        if self.editing_id:
            for i, farmer in enumerate(map_state.farmers):
                if farmer["id"] == self.editing_id:
                    map_state.farmers[i]["name"] = self.form_farmer_name
                    map_state.farmers[i]["cooperative_id"] = self.form_farmer_coop_id
                    break
            self.editing_id = None
        self.close_farmer_dialog()

    @rx.event
    async def save_farmer(self, form_data: dict):
        if self.editing_id:
            return await AdminState.update_farmer()
        return await AdminState.create_farmer()

    @rx.event
    def edit_farmer(self, farmer: Farmer):
        self.editing_id = farmer["id"]
        self.form_farmer_name = farmer["name"]
        self.form_farmer_coop_id = farmer["cooperative_id"]
        self.open_farmer_dialog()

    @rx.event
    async def delete_farmer(self, farmer_id: str):
        map_state = await self.get_state(MapState)
        map_state.farmers = [f for f in map_state.farmers if f["id"] != farmer_id]

    @rx.event
    def open_field_dialog(self):
        self.field_dialog_open = True

    @rx.event
    def close_field_dialog(self):
        self.field_dialog_open = False
        self.reset_field_form()

    @rx.event
    def reset_field_form(self):
        self.editing_id = None
        self.form_field_farmer_id = ""
        self.form_field_crop = ""
        self.form_field_area = ""
        self.form_field_polygon = ""

    def _parse_polygon(self, polygon_str: str) -> list[latlng]:
        try:
            return [
                latlng(lat=float(p.split(",")[0]), lng=float(p.split(",")[1]))
                for p in polygon_str.strip().split(";")
            ]
        except (ValueError, IndexError) as e:
            logging.exception(f"Error parsing polygon string: {e}")
            return []

    @rx.event
    async def create_field(self):
        map_state = await self.get_state(MapState)
        farmer = next(
            (f for f in map_state.farmers if f["id"] == self.form_field_farmer_id), None
        )
        if not farmer:
            return
        new_field: Field = {
            "id": f"field-{uuid.uuid4().hex[:6]}",
            "farmer_id": self.form_field_farmer_id,
            "farmer_name": farmer["name"],
            "crop": self.form_field_crop,
            "area": float(self.form_field_area) if self.form_field_area else 0.0,
            "polygon": self._parse_polygon(self.form_field_polygon),
        }
        self.close_field_dialog()
        return map_state.add_field(new_field)

    @rx.event
    async def update_field(self):
        map_state = await self.get_state(MapState)
        if self.editing_id:
            farmer = next(
                (f for f in map_state.farmers if f["id"] == self.form_field_farmer_id),
                None,
            )
            if not farmer:
                return
            updated_field: Field = {
                "id": self.editing_id,
                "farmer_id": self.form_field_farmer_id,
                "farmer_name": farmer["name"],
                "crop": self.form_field_crop,
                "area": float(self.form_field_area) if self.form_field_area else 0.0,
                "polygon": self._parse_polygon(self.form_field_polygon),
            }
            self.close_field_dialog()
            return map_state.update_field_data(updated_field)

    @rx.event
    async def save_field(self, form_data: dict):
        if self.editing_id:
            return await AdminState.update_field()
        return await AdminState.create_field()

    @rx.event
    def edit_field(self, field: Field):
        self.editing_id = field["id"]
        self.form_field_farmer_id = field["farmer_id"]
        self.form_field_crop = field["crop"]
        self.form_field_area = str(field["area"])
        self.form_field_polygon = ";".join(
            [f"{p.lat},{p.lng}" for p in field["polygon"]]
        )
        self.open_field_dialog()

    @rx.event
    async def delete_field(self, field_id: str):
        map_state = await self.get_state(MapState)
        return map_state.remove_field(field_id)

    @rx.event
    def open_poi_dialog(self):
        self.poi_dialog_open = True

    @rx.event
    def close_poi_dialog(self):
        self.poi_dialog_open = False
        self.reset_poi_form()

    @rx.event
    def reset_poi_form(self):
        self.editing_id = None
        self.form_poi_name = ""
        self.form_poi_type = "Warehouse"
        self.form_poi_lat = ""
        self.form_poi_lng = ""

    @rx.event
    async def create_poi(self):
        map_state = await self.get_state(MapState)
        new_poi: PointOfInterest = {
            "id": f"poi-{uuid.uuid4().hex[:6]}",
            "name": self.form_poi_name,
            "type": self.form_poi_type,
            "location": latlng(
                lat=float(self.form_poi_lat) if self.form_poi_lat else 0.0,
                lng=float(self.form_poi_lng) if self.form_poi_lng else 0.0,
            ),
        }
        self.close_poi_dialog()
        return map_state.add_poi(new_poi)

    @rx.event
    async def update_poi(self):
        map_state = await self.get_state(MapState)
        if self.editing_id:
            updated_poi: PointOfInterest = {
                "id": self.editing_id,
                "name": self.form_poi_name,
                "type": self.form_poi_type,
                "location": latlng(
                    lat=float(self.form_poi_lat) if self.form_poi_lat else 0.0,
                    lng=float(self.form_poi_lng) if self.form_poi_lng else 0.0,
                ),
            }
            self.close_poi_dialog()
            return map_state.update_poi_data(updated_poi)

    @rx.event
    async def save_poi(self, form_data: dict):
        if self.editing_id:
            return await AdminState.update_poi()
        return await AdminState.create_poi()

    @rx.event
    def edit_poi(self, poi: PointOfInterest):
        self.editing_id = poi["id"]
        self.form_poi_name = poi["name"]
        self.form_poi_type = poi["type"]
        self.form_poi_lat = str(poi["location"].lat)
        self.form_poi_lng = str(poi["location"].lng)
        self.open_poi_dialog()

    @rx.event
    async def delete_poi(self, poi_id: str):
        map_state = await self.get_state(MapState)
        return map_state.remove_poi(poi_id)

    def _get_farmer_by_name(self, name: str, farmers: list[Farmer]) -> Farmer | None:
        for farmer in farmers:
            if farmer["name"].lower() == name.lower():
                return farmer
        return None

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle the upload of a GeoJSON file."""
        self.is_uploading = True
        self.import_summary = None
        yield
        if not files:
            self.is_uploading = False
            self.import_summary = {
                "status": "Error",
                "message": "No file selected for upload.",
                "fields_added": 0,
                "farmers_added": 0,
            }
            return
        file = files[0]
        try:
            content = await file.read()
            data = json.loads(content)
            if data.get("type") != "FeatureCollection":
                raise ValueError("Invalid GeoJSON: Must be a FeatureCollection.")
            map_state = await self.get_state(MapState)
            current_farmers = map_state.farmers.copy()
            current_fields = map_state.fields.copy()
            new_farmers_count = 0
            new_fields_count = 0
            for feature in data.get("features", []):
                props = feature.get("properties", {})
                geom = feature.get("geometry", {})
                if not all(
                    [
                        props.get("farmer_name"),
                        props.get("crop"),
                        props.get("area"),
                        geom.get("type") == "Polygon",
                        geom.get("coordinates"),
                    ]
                ):
                    logging.warning(f"Skipping invalid feature: {feature}")
                    continue
                farmer_name = props["farmer_name"]
                farmer = self._get_farmer_by_name(farmer_name, current_farmers)
                if not farmer:
                    new_farmer_id = (
                        f"farmer-imported-{len(current_farmers) + 1}-{int(time.time())}"
                    )
                    farmer = {
                        "id": new_farmer_id,
                        "name": farmer_name,
                        "cooperative_id": map_state.cooperatives[0]["id"]
                        if map_state.cooperatives
                        else "coop-001",
                    }
                    current_farmers.append(farmer)
                    new_farmers_count += 1
                new_field_id = (
                    f"field-imported-{len(current_fields) + 1}-{int(time.time())}"
                )
                polygon_coords = geom["coordinates"][0]
                field = {
                    "id": new_field_id,
                    "farmer_id": farmer["id"],
                    "farmer_name": farmer["name"],
                    "crop": props["crop"],
                    "area": float(props["area"]),
                    "polygon": [latlng(lat=p[1], lng=p[0]) for p in polygon_coords],
                }
                current_fields.append(field)
                new_fields_count += 1
            map_state.farmers = current_farmers
            map_state.fields = current_fields
            self.import_summary = {
                "status": "Success",
                "message": "GeoJSON data imported successfully.",
                "fields_added": new_fields_count,
                "farmers_added": new_farmers_count,
            }
        except Exception as e:
            logging.exception(f"Error processing GeoJSON: {e}")
            self.import_summary = {
                "status": "Error",
                "message": f"An error occurred: {e}",
                "fields_added": 0,
                "farmers_added": 0,
            }
        finally:
            self.is_uploading = False