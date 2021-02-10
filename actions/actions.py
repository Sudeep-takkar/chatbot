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


class StudentAdmissionsFormValidator(FormValidationAction):
    """Validating admissions form input"""

    def name(self) -> Text:
        return "validate_student_admissions_form"

    # async def required_slots(
    #     self,
    #     slots_mapped_in_domain: List[Text],
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: Dict[Text, Any]
    # ) -> Optional[List[Text]]:
    #     print('required_slots')
    #     location = tracker.get_slot(
    #         "GPE")
    #     program = tracker.get_slot(
    #         "PROGRAM")
    #     institute = tracker.get_slot(
    #         "ORG")
    #     print('required_slots', institute, location, program)
    #     return []

    @staticmethod
    def institutions_db() -> Dict[str, List]:
        """Database of institutions"""
        return {
            "conestoga college",
            "university of waterloo"
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
            "ORG"), tracker.get_slot("GPE"), tracker.get_slot("PROGRAM"))
        location = tracker.get_slot(
            "GPE")
        program = tracker.get_slot(
            "PROGRAM")
        if slot_value and not isinstance(slot_value, list):
            if slot_value.lower() in self.institutions_db():
                return {"ORG": slot_value}
            else:
                dispatcher.utter_message(
                    template='utter_ORG_not_supported')
                return {"ORG": None}
        elif slot_value is None and (location is not None or program is not None):
            return {"ORG": ''}

        elif isinstance(slot_value, list):
            for i in slot_value:
                if i in self.institutions_db():
                    return {"ORG": i}
        else:
            dispatcher.utter_message(
                template='utter_ORG_not_supported')
            return {"ORG": None}
        return {"ORG": ''}

    def validate_PROGRAM(self,
                         slot_value: Text,
                         dispatcher: CollectingDispatcher,
                         tracker: Tracker,
                         domain: Dict[Text, Any]) -> Optional[Text]:
        """Validate Program"""
        print("inside validate_PROGRAM action", tracker.get_slot(
            "ORG"), tracker.get_slot("GPE"), tracker.get_slot("PROGRAM"))
        institute = tracker.get_slot(
            "ORG")
        location = tracker.get_slot(
            "GPE")
        if slot_value and not isinstance(slot_value, list):
            if slot_value.lower() in self.programs_db():
                return {"PROGRAM": slot_value}
            else:
                dispatcher.utter_message(
                    template='utter_PROGRAM_not_supported')
                return {"PROGRAM": None}
        elif slot_value is None and (institute is not None or location is not None):
            return {"PROGRAM": ''}

        elif isinstance(slot_value, list):
            for i in slot_value:
                if i in self.programs_db():
                    return {"PROGRAM": i}
        return {"PROGRAM": ''}

    def validate_GPE(self,
                     slot_value: Text,
                     dispatcher: CollectingDispatcher,
                     tracker: Tracker,
                     domain: Dict[Text, Any]) -> Optional[Text]:
        """Validate location/campus"""
        print("inside validate_GPE action", tracker.get_slot(
            "ORG"), tracker.get_slot("GPE"), tracker.get_slot("PROGRAM"))
        institution = tracker.get_slot(
            "ORG")
        program = tracker.get_slot(
            "PROGRAM")
        if slot_value and not isinstance(slot_value, list):
            if slot_value.lower() in self.locations_db():
                return {"GPE": slot_value}
            else:
                dispatcher.utter_message(
                    template='utter_GPE_not_supported')
                return {"GPE": None}
        elif slot_value is None and (institution is not None or program is not None):
            return {"GPE": ''}
        elif isinstance(slot_value, list):
            for i in slot_value:
                if i in self.locations_db():
                    return {"GPE": i}
        return {"GPE": ''}

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
        print('slot_dict.items()', slot_dict.items())
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
        program = tracker.get_slot("PROGRAM")
        slot_values = {
            "ORG": institution,
            "GPE": location,
            "PROGRAM": program
        }
        print('validate', location, institution, program)
        # extract requested slot
        slot_to_fill = tracker.get_slot("requested_slot")
        slot_value = tracker.get_slot(slot_to_fill)
        print('slot_to_fill', slot_to_fill, slot_value)

        if slot_value:
            if not isinstance(slot_value, list) and (slot_to_fill == 'PROGRAM' and slot_value.lower() not in self.programs_db()) or (slot_to_fill == 'GPE' and slot_value.lower() not in self.locations_db()) or (slot_to_fill == 'ORG' and slot_value.lower() not in self.institutions_db()):
                dispatcher.utter_message(
                    template="utter_{f}_not_supported".format(
                        f=slot_to_fill))
                return [SlotSet("requested_slot", slot_to_fill)]
            elif isinstance(slot_value, list):
                for i in slot_value:
                    if (i not in self.institutions_db() and slot_to_fill == 'ORG') or (i not in self.programs_db() and slot_to_fill == 'PROGRAM') or (i not in self.locations_db() and slot_to_fill == 'GPE'):
                        dispatcher.utter_message(
                            template="utter_{f}_not_supported".format(
                                f=slot_to_fill))
                        return [SlotSet("requested_slot", slot_to_fill)]

        if slot_to_fill:
            return [SlotSet("requested_slot", slot_to_fill)]

            # if not institution and (location is not None or program is not None):

            # reject to execute the form action
            # if some slot was requested but nothing was extracted
            # it will allow other policies to predict another action
            # raise ActionExecutionRejection(
            #     self.name(),
            #     f"Failed to extract slot {slot_to_fill} with action {self.name()}."
            #     f"Allowing other policies to predict next action.",
            # )
        return await self.validate_slots(slot_values, dispatcher, tracker, domain)


class ActionSubmitAdmissionsQuery(Action):
    def name(self) -> Text:
        return "action_admissions_query_submit"

    def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slots = {
            "ORG": None,
            "GPE": None,
            "PROGRAM": None
        }
        institution = tracker.get_slot("ORG")
        location = tracker.get_slot("GPE")
        program = tracker.get_slot("PROGRAM")
        print('action_admissions_query_submit', institution, location, program)

        if institution == '' and location == '' and program is None:
            dispatcher.utter_message(
                template="utter_ask_student_admissions_form_PROGRAM"
            )
            return [SlotSet("requested_slot", "PROGRAM")]
        if institution == '' and program == '' and location is None:
            dispatcher.utter_message(
                template="utter_ask_student_admissions_form_GPE"
            )
            return [SlotSet("requested_slot", "GPE")]

        if institution == None and program == '' and location == '':
            dispatcher.utter_message(
                template="utter_ask_student_admissions_form_ORG"
            )
            return [SlotSet("requested_slot", "ORG")]

        if institution is not None:
            if institution == 'conestoga college' or 'conestoga college' in institution:
                if program == 'mobile solutions development' or 'mobile solutions development' in program:
                    dispatcher.utter_message(
                        template="utter_program_query_success", PROGRAM='Mobile Solutions Development', ORG='Conestoga college', Link='https://www.conestogac.on.ca/fulltime/mobile-solutions-development/admissions?id=20866')
                    return [SlotSet(slot, value) for slot, value in slots.items()]
                if program == 'project management' or 'project management' in program:
                    dispatcher.utter_message(
                        template="utter_program_query_success", PROGRAM='Project Management', ORG='Conestoga college', Link='https://www.conestogac.on.ca/fulltime/project-management/admissions?id=20770')
                    return [SlotSet(slot, value) for slot, value in slots.items()]
                if program == 'computer applications development' or 'computer applications development' in program:
                    dispatcher.utter_message(
                        template="utter_program_query_success", PROGRAM='Computer Applications Development', ORG='Conestoga college', Link='https://www.conestogac.on.ca/fulltime/computer-applications-development/admissions?id=20395')
                    return [SlotSet(slot, value) for slot, value in slots.items()]
                dispatcher.utter_message(
                    template="utter_test_admissions_query_success", ORG='Conestoga college', Link='https://www.conestogac.on.ca/admissions')
                return [SlotSet(slot, value) for slot, value in slots.items()]
            if institution == 'university of waterloo' or 'university of waterloo' in institution:
                dispatcher.utter_message(
                    template="utter_test_admissions_query_success", ORG='University of Waterloo', Link='https://uwaterloo.ca/admissions/')
                return [SlotSet(slot, value) for slot, value in slots.items()]

        if location == 'ontario' or 'ontario' in location:
            dispatcher.utter_message(
                template="utter_test_admissions_query_ontario_success", ORG='Ontario', Link='https://www.ontariocolleges.ca/en/apply')
            return [SlotSet(slot, value) for slot, value in slots.items()]

        if program is not None:
            if program == 'mobile solutions development' or 'mobile solutions development' in program:
                dispatcher.utter_message(
                    template="utter_program_query_success", PROGRAM='Mobile Solutions Development', ORG='Conestoga college', Link='https://www.conestogac.on.ca/fulltime/mobile-solutions-development/admissions?id=20866')
                return [SlotSet(slot, value) for slot, value in slots.items()]
            if program == 'project management' or 'project management' in program:
                dispatcher.utter_message(
                    template="utter_program_query_success", PROGRAM='Project Management', ORG='Conestoga college', Link='https://www.conestogac.on.ca/fulltime/project-management/admissions?id=20770')
                return [SlotSet(slot, value) for slot, value in slots.items()]
            if program == 'computer applications development' or 'computer applications development' in program:
                dispatcher.utter_message(
                    template="utter_program_query_success", PROGRAM='Computer Applications Development', ORG='Conestoga college', Link='https://www.conestogac.on.ca/fulltime/computer-applications-development/admissions?id=20395')
                return [SlotSet(slot, value) for slot, value in slots.items()]

        return [SlotSet("requested_slot", "ORG")]


class StudentInformationForm(Action):
    def name(self) -> Text:
        return "student_information_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        # required_slots = ["ORG", "GPE"]
        highest_degree = tracker.slots.get("HIGHESTDEGREE")
        intake = tracker.slots.get("INTAKE")
        is_already_applied = tracker.slots.get("ISALREADYAPPLIED")
        name = tracker.slots.get("NAME")
        institution = tracker.slots.get("ORG")
        program = tracker.slots.get("PROGRAM")

        # print('inside student_admissions_form function' + institution, location)
        # if len(institution) != 0 or len(location) != 0 or len(program) != 0:
        #     return [SlotSet("requested_slot", None)]
        # elif len(institution) == 0:
        #     return [SlotSet("requested_slot", "ORG")]
        # return [SlotSet("requested_slot", None)]
