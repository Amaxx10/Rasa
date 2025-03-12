from typing import Any, Text, Dict, List, Union, Optional
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, ReminderScheduled, ReminderCancelled
from rasa_sdk.executor import CollectingDispatcher
from dateutil.parser import parse
from datetime import date, time
import datetime

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_say_data"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        travel_mode = tracker.get_slot("travel_mode")
        journey_type = tracker.get_slot("journey_type")
        source = tracker.get_slot("source")
        destination = tracker.get_slot("destination")
        departure_date = tracker.get_slot("departure_date")
        departure_time = tracker.get_slot("departure_time")
        arrival_date = tracker.get_slot("arrival_date")
        arrival_time = tracker.get_slot("arrival_time")
        no_of_people= tracker.get_slot("no_of_people")

        if journey_type in ["1", "one", "1-way", "1 way", "one way", "one-way", "single", "one-way trip", "one trip", "1 way trip", "single trip", "one way trip", "one-way trip"]:
            dispatcher.utter_message(text=f"Booking ticket for {no_of_people} person/people from {source} to {destination} via {travel_mode}. The journey type is a {journey_type} trip. Your departure journey will commence on {departure_date} at {departure_time}.")
        else: 
            dispatcher.utter_message(text=f"Booking ticket for {no_of_people} person/people from {source} to {destination} via {travel_mode}. The journey type is a {journey_type} trip. Your departure journey will commence on {departure_date} at {departure_time} and your arrival journey will begin on {arrival_date} at {arrival_time}.")

        dispatcher.utter_message(text="Have a nice journey !! :)")

        return []
    
class ActionSetReminder(Action):
    def name(self)-> Text:
        return "action_set_reminder"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text,Any])-> List[Dict[Text,Any]]:
        
        dispatcher.utter_message("Setting a reminder for 10 seconds")
        date= datetime.datetime.now() + datetime.timedelta(seconds=10)
        entities= tracker.latest_message.get("entities")

        reminder=ReminderScheduled(
            "EXTERNAL_reminder",
            trigger_date_time=date,
            entities=entities,
            name="my_reminder",
            kill_on_user_message=False
        )

        return[reminder]
    
class ActionReactToReminder(Action):
    def name(self) -> Text:
        return "action_react_to_reminder"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        print("aaaaa")

        name = tracker.get_slot("PERSON")
        if not name:
            name = "someone"

        dispatcher.utter_message(f"Remember to call {name}!")
        message=f"Remember to call {name}!"
        return []
    
class ValidateTravelForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_travel_form_1"
    
    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "source": [
                self.from_entity(entity="location", role= "source", intent=["book_ticket","inform_travel", "travel_form_1"])
            ],
            "destination": [
                self.from_entity(entity="location", role="destiantion", intent=["book_ticket","inform_travel", "travel_form_1"])
            ],
            "departure_date": [
                self.from_entity(entity="date", role="departure_date", intent=["book_ticket","inform_travel", "travel_form_1"])
            ],
            "departure_time": [
                self.from_entity(entity="time",role="departure_time", intent=["book_ticket","inform_travel", "travel_form_1"])
            ],
            "arrival_date": [
                self.from_entity(entity="date", role="arrival_date",  intent=["book_ticket","inform_travel", "travel_form_1"])
            ],
            "arrival_time": [
                self.from_entity(entity="time", role="arrival_time", intent=["book_ticket","inform_travel", "travel_form_1"])
            ],
            "PERSON":[
                self.from_text()
            ]
        }
    
    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any]
    ) -> List[Text]:
        required_slots = domain_slots.copy()
        journey_type = tracker.get_slot("journey_type")
        
        if journey_type in ["1", "one", "1-way", "1 way", "one way", "one-way", "single", "one-way trip", "one trip", "1 way trip", "single trip", "one way trip", "one-way trip"]:
            required_slots.remove("arrival_date")
            required_slots.remove("arrival_time")

        return required_slots
    def validate_journey_type(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        journey_type = tracker.get_slot("journey_type")
    
        if journey_type in ["1", "one", "1-way", "1 way", "one way", "one-way", "single", "one-way trip", "one trip", "1 way trip", "single trip", "one way trip", "one-way trip"]:
            dispatcher.utter_message(f"Journey set to one way")
            return {"journey_type": slot_value}
        elif journey_type in ["2", "two", "2-way", "2 way", "two way", "two-way", "round", "round way", "round trip", "return", "return trip", "two trip", "2 way trip", "two way trip", "two-way trip"]:
            dispatcher.utter_message(f"Journey set to round trip")
            return {"journey_type": slot_value}
        else:
            dispatcher.utter_message("Invalid trip type!!")
            return {"journey_type": None}
    
    
    
    # def validate_arrival_date(
    #     self,
    #     slot_value: Any,
    #     dispatcher: "CollectingDispatcher",
    #     tracker: "Tracker",
    #     domain: Dict[Text, Any]
    # ) -> List[Text]:
    #     journey_type=tracker.get_slot("journey_type")
    #     entities = tracker.latest_message.get("entities", [])
    #     for entity in entities:
    #         if entity['entity'] == 'date':
    #             dispatcher.utter_message(f"111111")
    #             if tracker.get_slot("departure_date") is None:
    #                 dispatcher.utter_message(f"aaaa")
    #                 # SlotSet("arrival_date", None)
    #                 # return {"departure_date": entity['value']}
    #                 return {"departure_date": entity['value'],"arrival_date": None}
    #             else:
    #                 if journey_type in ["1", "one", "1-way", "1 way", "one way", "one-way", "single", "one-way trip", "one trip", "1 way trip", "single trip", "one way trip", "one-way trip"]:
    #                     return {"arrival_date": None}
    #                 dispatcher.utter_message(f"bbbb")
    #                 return {"arrival_date": entity['value']}
    #     return[]

    # def validate_arrival_time(
    #     self,
    #     slot_value: Any,
    #     dispatcher: "CollectingDispatcher",
    #     tracker: "Tracker",
    #     domain: Dict[Text, Any]
    # ) -> List[Text]:
    #     journey_type=tracker.get_slot("journey_type")
    #     entities = tracker.latest_message.get("entities", [])
    #     for entity in entities:
    #         if entity['entity'] == 'time':
    #             dispatcher.utter_message(f"22222")
    #             if tracker.get_slot("departure_time") is None:
    #                 departure_time = entity['value']
    #                 return {"departure_time": entity['value'],"arrival_time": None}
    #             else:
    #                 if journey_type in ["1", "one", "1-way", "1 way", "one way", "one-way", "single", "one-way trip", "one trip", "1 way trip", "single trip", "one way trip", "one-way trip"]:
    #                     return {"arrival_time": None}
    #                 arrival_time = entity['value']
    #                 return {"arrival_time": entity['value']}
                
    def validate_travel_mode(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        travel_mode = tracker.get_slot("travel_mode")
        travel_mode_list = ["car", "cab", "taxi", "bus", "road", "train", "rail", "railway", "air", "plane", "flight", "aeroplane", "airplane", "sea", "water", "ship", "boat", "cruise"]
        if travel_mode in travel_mode_list:
            return {"travel_mode": slot_value}
        else:
            dispatcher.utter_message(text=f"Invalid Travel Mode: {travel_mode}. Please make sure there are no typos.")
            return {"travel_mode": None}

    def validate_no_of_people(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        no_of_people = tracker.get_slot("no_of_people")
        if no_of_people in ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]:
            return {"no_of_people": no_of_people}
        elif no_of_people in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
            return {"no_of_people": no_of_people}
        else:
            return {"no_of_people": no_of_people}

    def validate_source(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        source = tracker.get_slot("source")
        return {"source": slot_value}

    def validate_destination(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        source = tracker.get_slot("source")
        destination = tracker.get_slot("destination")
        if destination == source:
            dispatcher.utter_message(text="Invalid destination. Source and Destinations cannot be the same place.")
            return {"destination": None}
        else:
            return {"destination": slot_value}

    def validate_departure_date(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        today_date = date.today()
        try:
            departure_date = parse(slot_value, dayfirst=False).date()
            if departure_date >= today_date:
                return {"departure_date": departure_date.strftime("%Y-%m-%d")}
            else:
                dispatcher.utter_message(text="Invalid Departure Date. Departure Date cannot be before today's date.")
                return {"departure_date": None}
        except Exception as e:
            dispatcher.utter_message(text=f"Invalid Departure Date: {slot_value}. Please make sure there are no typos. Error: {str(e)}")
            return {"departure_date": None}

    def validate_departure_time(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        departure_time = tracker.get_slot("departure_time")
        try:
            departure_time = departure_time.split(' ')[0]
            if ':' not in departure_time:
                departure_time = departure_time + ':00'
            departure_time = parse(departure_time)
            departure_time = departure_time.time()
            dispatcher.utter_message(text="Setting departure time slot...")
            return {"departure_time": slot_value}
        except:
            dispatcher.utter_message(text="Invalid Departure Time. Please make sure there are no typos.")
            return {"departure_time": None}

    def validate_arrival_date(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        departure_date = tracker.get_slot("departure_date")
        try:
            arrival_date = parse(slot_value, dayfirst=False).date()
            if departure_date:
                parsed_departure_date = parse(departure_date).date()
                if arrival_date > parsed_departure_date:
                    return {"arrival_date": arrival_date.strftime("%Y-%m-%d")}
                else:
                    dispatcher.utter_message(text="Invalid Arrival Date. Arrival Date cannot be before the Departure Date.")
                    return {"arrival_date": None}
            else:
                return {"arrival_date": arrival_date.strftime("%Y-%m-%d")}
        except Exception as e:
            dispatcher.utter_message(text=f"Invalid Arrival Date: {slot_value}. Please make sure there are no typos. Error: {str(e)}")
            return {"arrival_date": None}

    def validate_arrival_time(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        arrival_time = tracker.get_slot("arrival_time")
        try:
            arrival_time = arrival_time.split(' ')[0]
            if ':' not in arrival_time:
                arrival_time = arrival_time + ':00'
            arrival_time = parse(arrival_time)
            arrival_time = arrival_time.time()
            dispatcher.utter_message(text="Setting arrival time slot...")
            return {"arrival_time": slot_value}
        except:
            dispatcher.utter_message(text="Invalid Arrival Time. Please make sure there are no typos.")
            return {"arrival_time": None}

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "source": [
                self.from_entity(entity="location", role= "source", intent=["book_ticket","inform_travel", "travel_form_1"])
            ],
            "destination": [
                self.from_entity(entity="location", role="destiantion", intent=["book_ticket","inform_travel", "travel_form_1"])
            ],
            "departure_date": [
                self.from_entity(entity="date", role="departure_date", intent=["book_ticket","inform_travel", "travel_form_1"])
            ],
            "departure_time": [
                self.from_entity(entity="time",role="departure_time", intent=["book_ticket","inform_travel", "travel_form_1"])
            ],
            "arrival_date": [
                self.from_entity(entity="date", role="arrival_date",  intent=["book_ticket","inform_travel", "travel_form_1"])
            ],
            "arrival_time": [
                self.from_entity(entity="time", role="arrival_time", intent=["book_ticket","inform_travel", "travel_form_1"])
            ]
        }
