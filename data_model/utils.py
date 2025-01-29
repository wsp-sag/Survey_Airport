"""
Utility functions used with the data model.
"""

from collections import defaultdict
from typing import Any, get_origin, get_args, Annotated, Optional
from enum import Enum, IntEnum
import pandas as pd
import enums as e

import geopandas as gpd
from shapely.geometry import Point

def map_zones(df, lat_col, long_col, shapefile, zone_column, external_zone_value):
    """
    Maps coordinates in a DataFrame to zones defined in a shapefile.

    Args:
        data (pd.DataFrame): Input DataFrame with latitude and longitude columns.
        lat_col (str): Column name for latitude in the DataFrame.
        long_col (str): Column name for longitude in the DataFrame.
        shapefile (str): Path to the shapefile containing zone geometries.
        zone_column (str): Column name in the shapefile that contains zone names.

    Returns:
        pd.Series: A Series with zone names mapped to each row in the DataFrame.
    """
    # Load the shapefile into a GeoDataFrame
    zones_gdf = gpd.read_file(shapefile)
    
    # Ensure the shapefile has a consistent CRS (WGS84)
    zones_gdf = zones_gdf.to_crs(epsg=4326)
    data = df.copy()
    # Add a geometry column to the DataFrame for spatial joining
    data["geometry"] = data.apply(
        lambda row: Point(row[long_col], row[lat_col]) 
        if pd.notnull(row[long_col]) and pd.notnull(row[lat_col]) else None, 
        axis=1
    )
    
    # Convert the DataFrame to a GeoDataFrame
    data_gdf = gpd.GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")
    
    # Perform a spatial join to map points to zones
    mapped_gdf = gpd.sjoin(data_gdf, zones_gdf, how="left", predicate="within")
    
    # Check if the zone_column is of integer type
    is_zone_int = pd.api.types.is_integer_dtype(zones_gdf[zone_column])
    
    # Map zone names, handling cases where coordinates are missing or no match is found
    def get_zone(row):
        if pd.isnull(row[lat_col]) or pd.isnull(row[long_col]):
            return None  # Blank if coordinates are missing
        elif pd.isnull(row[zone_column]):
            return external_zone_value # 99 for int zone_column, EXTERNAL for others
        else:
            return row[zone_column]  # Return the matched zone name

    # Apply the function to determine the zone for each row
    return mapped_gdf.apply(get_zone, axis=1)



def extract_base_type(typ):
    """
    Extracts base type from complex annotations. This is needed to identify whether a variable 
    is an Enum. Without this step, the origin of all the variables in the model is Annotated, even the variable is an Enum
    """
    origin = get_origin(typ)
    if origin is not Enum:      
        base = get_args(typ)
        if base:
           base = extract_base_type(base[0])
           return base
    return typ


def add_enum_label_columns(df,model):
    """
    After the datamodel output is converted into a dataframe, this method adds a column to the output dataframe for each Enum variable in the datamodel. This column 
    shows the Enum label.
    """
    
    for field, field_type in model.__annotations__.items():
        base_type = extract_base_type(field_type)
        if issubclass(base_type,(Enum,IntEnum)):
            enum_names = {item.value: item.name for item in base_type}
            enum_name_col = f"{field}_label" 
            df[enum_name_col] = df[field].map(enum_names).astype(str)
    return df


def add_list_objects(
    child_list: list,
    child_key: str,
    parent_list: list,
    parent_key: str,
    parent_variable: str,
) -> list:
    """
    Maps a list of child objects to a list of parent objects. The child objects
    are added to the parent objects as a list using the `parent_variable` as the
    key. The `child_key` is used to match the child to the parent using the
    `parent_key`.
    """
    parent_to_child_map = defaultdict(dict)
    for child in child_list:
        temp_key = child[child_key]
        del child[child_key]
        parent_to_child_map[temp_key] = child

    for parent in parent_list:
        temp_key = parent[parent_key]
        parent[parent_variable] = parent_to_child_map.get(temp_key, {})

    return parent_list


def nan_to_none(cls, value: Any):
    """
    Convert nan to none to address that missing strings were being read as nan, which resulted in a value error when using using Optional[str]
    """
    if value != value:
        return None
    return value


def military_to_clock(military_time):
    """Converts a military time string (HHMM) to a 12-hour clock format string (hh:mm AM/PM).

    Args:
        military_time: A string representing time in 24-hour format (e.g., "0600").

    Returns:
        A string representing time in 12-hour clock format (e.g., "6:00 AM").

    Raises:
        ValueError: If the input string is not in the correct format (HHMM).
    """

    if not military_time.isdigit() or len(military_time) != 4:
        raise ValueError(
            "Invalid military time format. Please use HHMM format (e.g., 0600)."
        )

    hours = int(military_time[:2])
    minutes = int(military_time[2:])

    # Convert to 12-hour format
    if hours == 0:
        clock_hours = 12
        period = "am"
    elif hours >= 12:
        clock_hours = hours - 12
        period = "pm"
    else:
        clock_hours = hours
        period = "am"

    # Format the output string
    return f"{clock_hours:02d}:{minutes:02d} {period}"


def add_synthetic_records(df):
    """
    Adds synthetic responses (arriving passengers corresponding to departing passengers) to the survey.
    Keeps Sociodemographics and other attributes same, exchanges trip based characteristics, like modes and origin, destination related attributes.
    """
     # Create a list to store synthetic records
    synthetic_records = []
    # Iterate through each record in the dataframe
    for index, row in df.iterrows():
        # Create a copy of the current row for the synthetic record
        if row['passenger_type'] == e.PassengerType.DEPARTING and row['is_completed'] == True:
            synthetic_record = row.copy()

            # Flip inbound/outbound
            synthetic_record['respondentid'] = 'syn-' + str(row['respondentid'])
            synthetic_record['inbound_or_outbound'] = 2 if row['inbound_or_outbound'] == 1 else 1
            synthetic_record['passenger_type'] = e.PassengerType.ARRIVING
            #to-do add resident_visitor_general:
            if row['resident_visitor_general'] == e.ResidentVisitorGeneral.GOING_HOME:
                synthetic_record['resident_visitor_general'] = e.ResidentVisitorGeneral.VISITING
            elif row['resident_visitor_general'] == e.ResidentVisitorGeneral.LEAVING_HOME:
                synthetic_record['resident_visitor_general'] = e.ResidentVisitorGeneral.COMING_HOME

            if row['passenger_segment'] == e.PassengerSegment.RESIDENT_DEPARTING:
                synthetic_record['passenger_segment'] = e.PassengerSegment.RESIDENT_ARRIVING
            elif row['passenger_segment'] == e.PassengerSegment.VISITOR_DEPARTING:
                synthetic_record['passenger_segment'] = e.PassengerSegment.VISITOR_ARRIVING

            synthetic_record['previous_flight_origin'], synthetic_record['next_flight_destination'] = row['next_flight_destination'], row['previous_flight_origin']

            # Flipping the main and reverse modes:
            if pd.notna(row['reverse_mode']):
                synthetic_record['main_mode'], synthetic_record['reverse_mode'] = row['reverse_mode'], row['main_mode']
            elif pd.notna(row['reverse_mode_predicted']):
                synthetic_record['main_mode'], synthetic_record['reverse_mode_predicted'] = row['reverse_mode_predicted'], row['main_mode']

            # Access and Egress Modes:
            synthetic_record['access_mode'], synthetic_record['egress_mode'] = row['egress_mode'], row['access_mode']

            # Activity Type
            synthetic_record['origin_activity_type'], synthetic_record['destination_activity_type'] = row['destination_activity_type'], row['origin_activity_type']
            synthetic_record['origin_activity_type_other'], synthetic_record['destination_activity_type_other'] = row['destination_activity_type_other'], row['origin_activity_type_other']
           
           #Location Attributes
            synthetic_record['origin_state'], synthetic_record['destination_state'] = row['destination_state'], row['origin_state']
            synthetic_record['origin_city'], synthetic_record['destination_city'] = row['destination_city'], row['origin_city']
            synthetic_record['origin_zip'], synthetic_record['destination_zip'] = row['destination_zip'], row['origin_zip']

            synthetic_record['origin_latitude'], synthetic_record['destination_latitude'] = row['destination_latitude'], row['origin_latitude']
            synthetic_record['origin_longitude'], synthetic_record['destination_longitude'] = row['destination_longitude'], row['origin_longitude']
            synthetic_record['origin_municipal_zone'], synthetic_record['destination_municipal_zone'] = row['destination_municipal_zone'], row['origin_municipal_zone']
            synthetic_record['origin_pmsa'], synthetic_record['destination_pmsa'] = row['destination_pmsa'], row['origin_pmsa']


            #synthetic_record['to_airport_transit_route_1'], synthetic_record['from_airport_transit_route_4'] = row['from_airport_transit_route_4'], row['to_airport_transit_route_1']
            #synthetic_record['to_airport_transit_route_2'], synthetic_record['from_airport_transit_route_3'] = row['from_airport_transit_route_3'], row['to_airport_transit_route_2']
            #synthetic_record['to_airport_transit_route_3'], synthetic_record['from_airport_transit_route_2'] = row['from_airport_transit_route_2'], row['to_airport_transit_route_3']
            #synthetic_record['to_airport_transit_route_4'], synthetic_record['from_airport_transit_route_1'] = row['from_airport_transit_route_1'], row['to_airport_transit_route_4']


            # Append the synthetic record to the list
            synthetic_record['record_type_synthetic'] = 1
            synthetic_records.append(synthetic_record)
    
    # Convert the list of synthetic records to a DataFrame
    synthetic_df = pd.DataFrame(synthetic_records)

    # Concatenate the original and synthetic dataframes
    combined_df = pd.concat([df, synthetic_df], ignore_index=True)

    return combined_df