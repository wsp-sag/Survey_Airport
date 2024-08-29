"""
Data Model for the SDIA Survey
"""

from datetime import datetime
from math import isnan
from typing import Annotated, Any, ClassVar, Literal, Optional, TypeVar, Union, List

from pydantic import (BaseModel, BeforeValidator, Field, computed_field,
                      field_validator, model_validator)
from pydantic_extra_types.coordinate import Coordinate, Latitude, Longitude

import enums as e


def coerce_nan_to_none(x: Any) -> Any:
    
    
    if isnan(x):
        return None
    return x


def coerce_nan_string_to_none(x: Any) -> Any:
    if x != x:
        return None
    return x


T = TypeVar("T")

NoneOrNan = Annotated[Optional[T], BeforeValidator(coerce_nan_to_none)]
NoneOrNanString = Annotated[Optional[T], BeforeValidator(coerce_nan_string_to_none)]


class PydanticModel(BaseModel):
    """
    Base class for all Pydantic models, create in case future modifications are helpful
    """


class Lat(BaseModel):
    lat: Latitude
    """Latitude"""

class Lng(BaseModel):
    lng: Longitude
    """Longitude"""

class Coord(BaseModel):
    coord: Coordinate

class Trip(PydanticModel):
    """
    Data model for a trip taken by a respondent.
    """

    inbound_or_outbound: NoneOrNan[e.InboundOutbound] = Field(
        ...,
        description="Whether the trip is inbound to the airport or outbound from the airport.",
    )
    """
    Whether the trip is inbound to the airport or outbound from the airport.
    """

    main_mode: NoneOrNanString[Union[e.TravelMode, str]] = Field(
        ..., description = "Main Mode to/from airport."
    )
    """
    Main Mode to/from airport.
    """

    trip_start_time: NoneOrNan[e.DepartTime] = Field(
        ..., description="Start time of the trip."
    )
    """
    Start time of the trip.
    """

    trip_arrival_time: NoneOrNan[e.DepartTime] = Field(
        ..., description="Arrival time of the trip."
    )
    """
    Arrival time of the trip.
    """

    origin_activity_type: NoneOrNanString[Union[e.ActivityType, str]] = Field(
        ..., description="Activity type at the origin of the trip to the airport."
    )
    """
    Activity type at the origin of the trip to the airport.
    """

    origin_name: NoneOrNanString[Optional[str]] = Field(
        ..., description="Place name of the origin of the trip to the airport."
    )
    """
    Place name of the origin of the trip to the airport.
    """

    origin_location: NoneOrNan[Coord] = Field(
        ..., description="Longitude and latitude of inbound trip origin."
    )
    """
    Longitude and latitude of inbound trip origin.
    """

    destination_activity_type: NoneOrNanString[Union[e.ActivityType, str]] = Field(
        ...,
        description="Activity type at the destination of the trip from the airport.",
    )
    """
    Activity type at the destination of the trip from the airport.
    """

    destination_name: NoneOrNanString[Optional[str]] = Field(
        ..., description="Place name of the destination of the trip from the airport."
    )
    """
    Place name of the origin of the trip to the airport.
    """

    destintation_location: NoneOrNan[Coord] = Field(
        ..., description="Longitude and latitude of outbound trip destination."
    )
    """
    Longitude and latitude of outbound trip destination.
    """

    number_transit_vehicles: NoneOrNan[int] = Field(
        ..., description="Number of transit vehicles."
    )
    """
    Number of transit vehicles.
    """

    transit_route: NoneOrNan[str] = Field(
        ..., description="For each transit vehicle, name of route."
    )
    """
    For each transit vehicle, name of route.
    """

    transit_boarding: List[NoneOrNan[Coord]] = Field(
        ..., description="For each transit vehicle , longitude and latitude of boarding location. "
    )
    """
    For each transit vehicle , longitude and latitude of boarding location. 
    """

    mode_sequence: List[NoneOrNanString[Union[e.TravelMode, str]]] = Field(
        ..., description="Sequence of modes used to travel to or from the airport."
    )
    """
    Sequence of modes used to travel to or from the airport.
    """

    access_mode: NoneOrNanString[Union[e.TravelMode, str]] = Field(
        ..., description = "Access mode to first transit vehicle for inbound trip."
    )
    """
    Access mode to first transit vehicle for inbound trip.
    """

    egress_mode: NoneOrNanString[Union[e.TravelMode, str]] = Field(
        ..., description = "Egress mode from last transit vehicle for outbound trip."
    )
    """
    Egress mode from last transit vehicle for outbound trip.
    """
 
    taxi_fhv_fare: NoneOrNan[float] = Field(
        ..., description = "Taxi or for-hire vehicle fare."
    )
    """
    Taxi or for-hire vehicle fare.
    """

    taxi_fhv_wait: NoneOrNan[float] = Field(
        ..., description = "Wait time for taxi or for-hire vehicle."
    )
    """
    Wait time for taxi or for-hire vehicle.
    """

    parking_location: NoneOrNanString[Union[e.ParkingLocation, str]] = Field(
        ..., description = "Name (and/or longitude and latitude) of respondent's parking location. "
    )
    """
    Name (and/or longitude and latitude) of respondent's parking location. 
    """

    parking_cost: NoneOrNan[float] = Field(
        ..., description = "Amount respondent paid to park."
    )
    """
    Amount respondent paid to park.
    """

    parking_cost_frequency: NoneOrNan[e.ParkingCostFrequency] = Field(
        ..., description = "Frequency of reported parking cost (e.g., one-time, per hour, per day, per month)"
    )
    """
    Frequency of reported parking cost (e.g., one-time, per hour, per day, per month)
    """

    reimbursement: NoneOrNan[e.ParkingReimbursement] = Field(
        ..., description = "Whether or not ground access cost will be reimbursed by employer or other non-household member."
    )
    """
    Whether or not ground access cost will be reimbursed by employer or other non-household member.
    """


class Respondent(PydanticModel):
    """
    Data model for a survey respondent. It includes attributes common to air passengers and employees.
    """

    respondent_id: NoneOrNan[int] = Field(..., description="Unique identifier for the respondent.")
    """
    Unique identifier for the respondent.
    """

    interview_location: NoneOrNan[e.InterviewLocation] = Field(..., description = "Location where respondent was intercepted.")
    """
    Location where respondent was intercepted.
    """

    datetime_completed: NoneOrNanString[str]
    """
    Date and time that respondent completed the survey
    """

    market_segment: NoneOrNan[e.Type] = Field(
        ..., description="Type of respondent, either passenger, employee, or other."
    )
    """
    Type of respondent, either passenger, employee, or other.
    """

    is_qualified_age: NoneOrNanString[bool] = Field(
        ...,
        description="Whether the respondent is of a qualified age to participate in the survey.",
    )
    """
    Whether the respondent is of a qualified age to participate in the survey.
    """

    is_qualified_not_connecting: NoneOrNanString[bool] = Field(
        ...,
        description="Whether the respondent is traveling to the airport and therefore qualified to participate in the survey.",
    )
    """
    Whether the respondent is traveling to the airport and therefore 
    """

    resident_visitor_general: NoneOrNan[e.ResidentVisitorGeneral] = Field(
        ...,
        description="Whether a resident or a visitor of the San deigo airport service area.",
    )
    """
    Whether a resident or a visitor of the San deigo airport service area.
    """

    resident_visitor_followup: NoneOrNanString[bool] = Field(
        ...,
        description="If neither a resident or a visitor, whether the respondent is visiting San Diego.",
    )
    """
    If neither a resident or a visitor, whether the respondent is visiting San Diego.
    """

    resident_visitor: NoneOrNan[e.ResidentVisitor] = Field(
        ...,
        description="Where the respondent resides in the airport service area most of the year.",
    )
    """
    Where the respondent resides in the airport service area most of the year.
    """

    country_of_residence: NoneOrNan[e.Country] = Field(
        ...,
        description="Country of residence for international vistors.",
    )
    """
    Country of residence for international vistors.
    """

    state_of_residence: NoneOrNan[e.State] = Field(
        ...,
        description="State of residence for US and Mexico residents.",
    )
    """
    State of residence for US and Mexico residents.
    """

    home_location: NoneOrNan[Coord] = Field(..., description="Respondent's home location")
    """
    Respondent's home location.
    """

    age: NoneOrNan[e.Age] = Field(..., description="Age category of the respondent.")
    """
    Age category of the respondent.
    """

    gender: NoneOrNan[e.Gender] = Field(..., description="Gender of the respondent.")
    """
    Gender of the respondent.
    """

    race_aian: NoneOrNanString[bool] = Field(
        ...,
        description="Does the respondent identify as American Indian or Alaska Native?",
    )
    """
    Does the respondent identify as American Indian or Alaska Native?
    """

    race_asian:  NoneOrNanString[bool] = Field(..., description="Does the respondent identify as Asian?")
    """
    Does the respondent identify as Asian?
    """

    race_black:  NoneOrNanString[bool] = Field(
        ..., description="Does the respondent identify as Black or African American?"
    )
    """
    Does the respondent identify as Black or African American?
    """

    race_hispanic:  NoneOrNanString[bool] = Field(
        ..., description="Does the respondent identify as Hispanic or Latino?"
    )
    """
    Does the respondent identify as Hispanic or Latino?
    """

    race_middle_eastern:  NoneOrNanString[bool] = Field(
        ..., description="Does the respondent identify as Middle Eastern?"
    )
    """
    Does the respondent identify as Middle Eastern?
    """

    race_hp:  NoneOrNanString[bool] = Field(
        ...,
        description="Does the respondent identify as Native Hawaiian or Other Pacific Islander?",
    )
    """
    Does the respondent identify as Native Hawaiian or Other Pacific Islander?
    """

    race_white:  NoneOrNanString[bool] = Field(..., description="Does the respondent identify as White?")
    """
    Does the respondent identify as White?
    """

    race_unknown:  NoneOrNanString[bool] = Field(
        ..., description="Does the respondent identify as an unknown"
    )
    """
    Does the respondent identify as an unknown race/ethnicity?
    """

    race_other: NoneOrNanString[str] = Field(
        ...,
        description="If the respondent enters a race/ethnicicy not listed above, this field will be populated.",
    )
    """
    If the respondent enters a race/ethnicity not listed above, this field will be populated. 
    """

    number_persons_in_household: NoneOrNan[e.HouseholdSize] = Field(
        ..., description="Number of persons in the respondent's household."
    )
    """
    Number of persons in the respondent's household.
    """

    number_vehicles: NoneOrNan[e.HouseholdVehicles] = Field(
        ..., description="Number of vehicles in the respondent's household."
    )
    """
    Number of vehicles in the respondent's household.
    """

    household_income: NoneOrNan[e.HouseholdIncome] = Field(
        ..., description="Income range of the respondent's household."
    )
    """
    Income range of the respondent's household.
    """

    is_income_below_poverty: NoneOrNanString[bool] = Field(
        ..., description="Does the respondent speak a language other than English at home?",
    )
    """
    Does the respondent speak a language other than English at home?
    """

    number_of_workers: NoneOrNan[e.HouseholdWorkers] = Field(
        ..., description="Number of workers in the respondent's household."
    )
    """
    Number of workers in the respondent's household.
    """

    other_home_language: NoneOrNanString[bool] = Field(
        ..., description = "Does the respondent speak a language other than English at home?",
    )
    """
    Does the respondent speak a language other than English at home?
    """

    english_proficiency: NoneOrNan[e.EnglishProficiency] = Field(
        ..., description="Respondent's level of English proficiency."
    )
    """
    Respondent's level of English proficiency.
    """

    trip: Trip = Field(..., description="Details of the trip taken by the respondent.")
    """
    Details of the trip taken by the respondent.
    """

    @model_validator(mode="after")
    def prefer_not_disclose_is_unique(cls, values):
        race_unknown = values.race_unknown
        race_aian = values.race_aian
        race_asian = values.race_asian
        race_black = values.race_black
        race_hispanic = values.race_hispanic
        race_middle_eastern = values.race_middle_eastern
        race_white = values.race_white
        if race_unknown and (
            race_aian
            or race_asian
            or race_black
            or race_hispanic
            or race_middle_eastern
            or race_white
        ):
            raise (ValueError("Prefer not to disclose cannot be combined with any race"))


class Employee(Respondent):
    """
    Data model for an employee respondent. It includes attributes specific to employees.
    """

    shift_start_location: NoneOrNan[Coord] = Field(
        ..., description = "Longitude and Latitude of building where the employee starts their shift."
    )
    """
    Longitude and Latitude of building where the employee starts their shift.
    """

    shift_start_airport_building: NoneOrNanString[Union[e.SanBuildings, str]] = Field(
        ..., description = "Name of building where employee starts their shift."
    )
    """
    Name of building where employee starts their shift.
    """

    employer: NoneOrNanString[Union[e.Employers, str]] = Field(
        ..., description = "Name of respondent's employer."
    )
    """
    Name of  respondent's employer.
    """

    occupation: NoneOrNanString[Union[e.Occupations, str]] = Field(
        ..., description = "Occupation of the employee."
    )
    """
    Occupation of the employee.
    """

    number_hours_worked: NoneOrNan[e.HoursWorked] = Field(
        ..., description = "Number of hours respondent worked in the past 7 days."
    )
    """
    Number of hours respondent worked in the past 7 days.
    """

    number_commute_days: NoneOrNan[e.CommuteDays] = Field(
        ..., description = "Number of days respondent commuted to the airport in the past 7 days."
    )
    """
    Number of days respondent commuted to the airport in the past 7 days.
    """

    shift_start_time: NoneOrNan[e.DepartTime] = Field(
        ..., description = "Time when the employee's shift starts."
    )
    """
    Time when the employee's shift starts.
    """

    shift_end_time: NoneOrNan[e.DepartTime] = Field(
        ..., description = "Time when the employee's shift ends."
    )
    """
    Time when the employee's shift ends.
    """
    
    reverse_commute_mode: NoneOrNan[e.TravelMode] = Field(
        ..., description = "Reverse commute mode."
    )
    """
    Reverse commute mode.
    """

    past_commute_modes: List[NoneOrNan[e.TravelMode]] = Field(
        ..., description = "Modes used to commute to SDIA in the past 12 months."
    )
    """
    Modes used to commute to SDIA in the past 12 months.
    """

    alternative_commute_modes: List[NoneOrNan[e.TravelMode]] = Field(
        ..., description = "Modes used to travel to SDIA in the past 30 days."
    )
    """
    Modes used to travel to SDIA in the past 30 days.
    """

    commute_mode_decision: List[NoneOrNan[e.CommuteModeDecision]] = Field(
        ..., description = "Factors affecting mode choice, for respondents who do not always use the same mode."
    )
    """
    Factors affecting mode choice, for respondents who do not always use the same mode.
    """

    employee_parking: NoneOrNanString[bool] = Field(
        ..., description = "Whether the respondent has access to employee parking."
    )
    """
    Whether the respondent has access to employee parking.
    """


class AirPassenger(Respondent):
    """
    Data model for an air passenger respondent. It includes attributes specific to air passengers.
    """

    next_flight_destination: NoneOrNanString[str] = Field(
        ..., description = "Destination of the flight for departing passengers."
    )
    """
    Destination of the flight for departing passengers.
    """

    previous_flight_origin: NoneOrNanString[str] = Field(
        ..., description = "Origin of the flight for arriving passengers."
    )
    """
    Origin of the flight for arriving passengers.
    """

    airline: NoneOrNanString[Union[e.Airline, str]] = Field(
        ..., description = "Airline of the respondent's flight."
    )
    """
    Airline of the respondent's flight.
    """

    flight_number: NoneOrNanString[str] = Field(
        ..., description = "Flight number of the respondent's flight."
    )
    """
    Flight number of the respondent's flight.
    """

    is_final_destination: NoneOrNanString[bool] = Field(
        ..., description = "Whether respondent's next destination is their final destination."
    )
    """
    Whether respondent's next destination is their final destination.
    """

    final_flight_destination: NoneOrNanString[str] = Field(
        ..., description = "Final destination of the flight for departing passengers."
    )
    """
    Final destination of the flight for departing passengers.
    """

    flight_departure_time: NoneOrNan[e.DepartTime] = Field(
        ..., description = "Time of flight departure."
    )
    """
    Time of flight departure.
    """

    flight_arrival_time: NoneOrNan[e.DepartTime] = Field(
        ..., description = "Time of flight arrival."
    )
    """
    Time of flight arrival.
    """

    is_original_origin: NoneOrNanString[bool] = Field(
        ..., description = "Whether the respondent used a connecting flight."
    )
    """
    Whether the respondent used a connecting flight.
    """

    original_flight_origin: NoneOrNanString[str] = Field(
        ..., description = "Original origin for arriving passengers."
    )
    """
    Original origin for arriving passengers.
    """

    flight_purpose: NoneOrNanString[Union[e.FlightPurpose, str]] = Field(
        ..., description = "Purpose of the respondent's flight."
    )
    """
    Purpose of the respondent's flight.
    """
    
    convention_center: NoneOrNanString[bool] = Field(
        ..., description = "Whether the visitor went/going to convention center."
    )
    """
    Whether the visitor went/going to convention center.
    """

    convention_center_activity: NoneOrNanString[Union[e.ConventionCenterActivity, str]] = Field(
        ..., description = "Type of activity that the respondent conducted at the convention center."
    )
    """
    Type of activity that the respondent conducted at the convention center.
    """

    checked_bags: NoneOrNan[e.CheckedBags] = Field(
        ..., description = "Number of checked bags."
    )
    """
    Number of checked bags.
    """

    carryon_bags: NoneOrNan[e.CarryOns] = Field(
        ..., description = "Number of carry-on bags."
    )
    """
    Number of carry-on bags.
    """

    nights_away: NoneOrNan[e.TravelDuration] = Field(
        ..., description = "Number of nights the departing air passengers will be away."
    )
    """
    Number of nights the departing air passengers will be away.
    """

    nights_visited: NoneOrNan[e.TravelDuration] = Field(
        ..., description = "Number of nights the arriving air passengers will be in the San Diego Region."
    )
    """
    Number of nights the arriving air passengers will be in the San Diego Region.
    """

    party_size_flight: NoneOrNanString[Union[e.PartySize, str]] = Field(
        ..., description = "Size of the party flying with the respondent (count includes the respondent)."
    )
    """
    Size of the party flying with the respondent (count includes the respondent).
    """

    party_size_ground_access_same: NoneOrNanString[bool] = Field(
        ..., description = "Whether flying party all traveled to airport together"
    )
    """
    Whether flying party all traveled to airport together
    """

    party_size_ground_access: NoneOrNanString[Union[e.PartySize, str]] = Field(
        ..., description = "Size of ground access travel party."
    )
    """
    Size of ground access travel party.
    """

    party_includes_child_aged00to02: NoneOrNanString[bool] = Field(
        ..., description = "True if the traveling party includes a child aged zero to two."
    )
    """
    True if the traveling party includes a child aged zero to two.
    """

    party_includes_child_aged03to09: NoneOrNanString[bool] = Field(
        ..., description = "True if the traveling party includes a child aged three to nine."
    )
    """
    True if the traveling party includes a child aged three to nine.
    """

    party_includes_child_aged10to12:  NoneOrNanString[bool] = Field(
        ..., description = "True if the traveling party includes a child aged ten to twelve."
    )
    """
    True if the traveling party includes a child aged ten to twelve.
    """

    party_includes_child_aged13to17:  NoneOrNanString[bool] = Field(
        ..., description = "True if the traveling party includes a child aged thirteen to seventeen."
    )
    """
    True if the traveling party includes a child aged thirteen to seventeen.
    """

    party_includes_coworker: NoneOrNanString[bool] = Field(
        ..., description = "True if the traveling party includes a coworker."
    )
    """
    True if the traveling party includes a coworker.
    """

    party_includes_friend_relative:  NoneOrNanString[bool] = Field(
        ..., description = "True if the traveling party includes a friend or relative."
    )
    """
    True if the traveling party includes a friend or relative.
    """

    sdia_flight_frequency: NoneOrNan[e.SanFlightFrequency] = Field(
        ..., description = "Respondent's number of flights from SDIA in the past 12 months."
    )
    """
    Respondent's number of flights from SDIA in the past 12 months.
    """

    sdia_previous_accessmode: NoneOrNan[e.SanFlightFrequency] = Field(
        ..., description = "Number of times respondent used revealed access modes for other SDIA airport access trips in the past 12 months."
    )
    """
    Number of times respondent used revealed access modes for other SDIA airport access trips in the past 12 months.
    """

    sdia_accessmode_split: List[NoneOrNan[e.TravelMode]] = Field(
        ..., description = "Other modes used to travel to SDIA in the past 12 months."
    )
    """
    Other modes used to travel to SDIA in the past 12 months.
    """

    sdia_accessmode_decision: List[NoneOrNan[e.CommuteModeDecision]] = Field(
        ..., description = "Factors affecting mode choice, for respondents who do not always used the same mode."
    )
    """
    Factors affecting mode choice, for respondents who do not always used the same mode.
    """

    reverse_mode: NoneOrNan[e.TravelMode] = Field(
        ..., description = "Mode that was used in the reverse direction."
    )
    """
    Mode that was used in the reverse direction.
    """

    reverse_mode: NoneOrNanString[Union[e.TravelMode, str]] = Field(
        ..., description = "Mode that will be used in the reverse direction."
    )
    """
    Mode that will be used in the reverse direction.
    """

    sdia_transit_awareness: NoneOrNanString[bool] = Field(
        ..., description = "Whether respondent is aware that buses are serving SDIA."
    )
    """
    Whether respondent is aware that buses are serving SDIA
    """

    reasons_no_transit: List[NoneOrNan[e.ReasonsNoTransit]] = Field(
        ..., description = "Reasons for not using transit for trip to/from airport"
    )
    """
    Reasons for not using transit for trip to/from airport
    """

    general_use_transit_resident: NoneOrNan[e.TransitUseFrequency] = Field(
        ..., description = "General transit use frequency by residents of San Diego region in San Diego region."
    )
    """
    General transit use frequency by residents of San Diego region in San Diego region.
    """

    general_use_transit_visitor_home: NoneOrNan[e.TransitUseFrequency] = Field(
        ..., description = "General transit use frequency by visitors of San Diego region when home."
    )
    """
    General transit use frequency by visitors of San Diego region when home.
    """

    general_modes_used_visitor: List[NoneOrNan[e.TravelMode]] = Field(
        ..., description = "Modes respondent used during visit of San Diego region."
    )
    """
    Modes respondent used during visit of San Diego region.
    """

    non_sdia_flight_frequency: NoneOrNan[e.SanFlightFrequency] = Field(
        ..., description = "Respondent's number of flights from airport other than SDIA in the past 12 months."
    )
    """
    Respondent's number of flights from airport other than SDIA in the past 12 months.
    """

    airport_access_transit_use_elsewhere: NoneOrNanString[bool] = Field(
        ..., description = "Whether respondent used transit to access other airports."
    )
    """
    Whether respondent used transit to access other airports.
    """

    airport_access_transit_name: NoneOrNan[str] = Field(
        ..., description = "Names of airports accessed by transit."
    )
    """
    Names of airports accessed by transit.
    """

