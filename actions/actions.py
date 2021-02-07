# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Union, Optional
import logging
from rasa_sdk import Action, Tracker, FormValidationAction, utils
from rasa_sdk.events import (SlotSet,
                             EventType, SessionStarted, ActionExecuted,     Restarted,
                             FollowupAction)
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_sdk.executor import CollectingDispatcher
import warnings
from rasa_sdk.interfaces import Action, ActionExecutionRejection
import inspect

logger = logging.getLogger(__name__)


class StudentAdmissionsForm(Action):
    def name(self) -> Text:
        return "student_admissions_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        # required_slots = ["ORG", "GPE"]
        institution = tracker.slots.get("ORG")
        location = tracker.slots.get("GPE")
        program = tracker.slots.get("PROGRAM")

        print('inside student_admissions_form function' + institution, location)
        if len(institution) != 0 or len(location) != 0:
            return [SlotSet("requested_slot", None)]
        elif len(institution) == 0:
            return [SlotSet("requested_slot", "ORG")]
        return [SlotSet("requested_slot", None)]


class StudentAdmissionsFormValidator(FormValidationAction):
    """Validating admissions form input"""

    def name(self) -> Text:
        return "validate_student_admissions_form"

    @staticmethod
    def institutions_db() -> Dict[str, List]:
        """Database of institutions"""
        return {
            "conestoga college",
            "university of waterloo",
            "university of guelph",
            "wilfred laurier university",
        }

    @staticmethod
    def programs_db() -> Dict[str, List]:
        """Database of programs"""
        return {
            "mobile solutions development",
            "computer applications development",
            "project management"
        }

    @staticmethod
    def locations_db() -> Dict[str, List]:
        """Database of locations"""
        return {
            "ontario"
        }

    def validate_ORG(self,
                     slot_value: Text,
                     dispatcher: CollectingDispatcher,
                     tracker: Tracker,
                     domain: Dict[Text, Any]) -> Optional[Text]:
        """Validate Educational ORG/institutions"""
        print("inside validate_ORG action", tracker.get_slot(
            "ORG"), tracker.get_slot("GPE"))
        location = tracker.get_slot(
            "GPE")
        if slot_value and not isinstance(slot_value, list):
            if slot_value.lower() in self.institutions_db():
                return {"ORG": slot_value}
            else:
                dispatcher.utter_message(
                    template='utter_institute_not_supported')
                return {"ORG": None}
        elif slot_value is None and location is not None:
            return {"ORG": ""}

        elif isinstance(slot_value, list):
            for i in slot_value:
                if i in self.institutions_db():
                    return {"ORG": i}
        else:
            dispatcher.utter_message(
                template='utter_institute_not_supported')
            return {"ORG": None}

    def validate_GPE(self,
                     slot_value: Text,
                     dispatcher: CollectingDispatcher,
                     tracker: Tracker,
                     domain: Dict[Text, Any]) -> Optional[Text]:
        """Validate location/campus"""
        print("inside validate_GPE action", tracker.get_slot(
            "ORG"), tracker.get_slot("GPE"), slot_value)
        institution = tracker.get_slot(
            "ORG")
        if slot_value and not isinstance(slot_value, list):
            if slot_value.lower() in self.locations_db():
                return {"GPE": slot_value}
            else:
                dispatcher.utter_message(
                    template='utter_location_not_supported')
                return {"GPE": None}
        elif slot_value is None and institution is not None:
            print("CONDITION MATCHED")
            return {"GPE": ""}
        elif isinstance(slot_value, list):
            print('condition matched')
            for i in slot_value:
                if i in self.locations_db():
                    return {"GPE": i}

    async def validate_slots(
        self,
        slot_dict: Dict[Text, Any],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[EventType]:
        """Validate slots using helper validation functions.

        Call validate_{slot} function for each slot, value pair to be validated.
        If this function is not implemented, set the slot to the value.
        """

        for slot, value in list(slot_dict.items()):
            validate_func = getattr(
                self, f"validate_{slot}", lambda *x: {slot: value})
            if inspect.iscoroutinefunction(validate_func):
                validation_output = await validate_func(
                    value, dispatcher, tracker, domain
                )
            else:
                validation_output = validate_func(
                    value, dispatcher, tracker, domain)
            if not isinstance(validation_output, dict):
                warnings.warn(
                    "Returning values in helper validation methods is deprecated. "
                    + f"Your `validate_{slot}()` method should return "
                    + "a dict of {'slot_name': value} instead."
                )
                validation_output = {slot: validation_output}
            slot_dict.update(validation_output)
            print('slot_dict', slot_dict, validation_output)
        # validation succeed, set slots to extracted values
        return [SlotSet(slot, value) for slot, value in slot_dict.items()]

    async def validate(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        # slot_values = self.extract_other_slots(dispatcher, tracker, domain)
        location = tracker.get_slot("GPE")
        institution = tracker.get_slot("ORG")
        slot_values = {
            "ORG": institution,
            "GPE": location
        }
        print('validate', location, institution)
        # extract requested slot
        slot_to_fill = tracker.get_slot("requested_slot")
        print('slot_to_fill', slot_to_fill)
        if slot_to_fill:
            [SlotSet("requested_slot", slot_to_fill)]

            if not (location or institution):
                # reject to execute the form action
                # if some slot was requested but nothing was extracted
                # it will allow other policies to predict another action
                raise ActionExecutionRejection(
                    self.name(),
                    f"Failed to extract slot {slot_to_fill} with action {self.name()}."
                    f"Allowing other policies to predict next action.",
                )
        return await self.validate_slots(slot_values, dispatcher, tracker, domain)


class ActionSubmitAdmissionsQuery(Action):
    def name(self) -> Text:
        return "action_admissions_query_submit"

    def run(self, dispatcher, tracker: Tracker, domain: "DomainDict") -> List[Dict[Text, Any]]:
        slots = {
            "ORG": None,
            "GPE": None
        }
        institution = tracker.get_slot("ORG")
        location = tracker.get_slot("GPE")
        print(institution, location)

        if institution == 'conestoga college':
            print('conestoga college')
            dispatcher.utter_message(
                template="utter_test_admissions_query_success", ORG='Conestoga college', Link='https://www.conestogac.on.ca/admissions')
            return [SlotSet(slot, value) for slot, value in slots.items()]

        if institution == 'university of waterloo':
            print('university of waterloo')
            dispatcher.utter_message(
                template="utter_test_admissions_query_success", ORG='University of Waterloo', Link='https://uwaterloo.ca/admissions/')
            return [SlotSet(slot, value) for slot, value in slots.items()]

        if location == 'ontario':
            dispatcher.utter_message(
                template="utter_test_admissions_query_ontario_success", ORG='Ontario', Link='https://www.ontariocolleges.ca/en/apply')
            return [SlotSet(slot, value) for slot, value in slots.items()]
        return [SlotSet("requested_slot", "ORG")]
