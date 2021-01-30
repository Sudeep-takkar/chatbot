# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Union, Optional
import logging
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import (SlotSet,
                             EventType, SessionStarted, ActionExecuted,     Restarted,
                             FollowupAction)
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_sdk.executor import CollectingDispatcher


logger = logging.getLogger(__name__)


class StudentAdmissionsForm(Action):
    def name(self) -> Text:
        return "student_admissions_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        # required_slots = ["ORG", "GPE"]
        print('inside student_admissions_form function' + tracker.slots.get("ORG"))
        if tracker.slots.get("ORG") is None:
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

    # @staticmethod
    # def institution_campus_db() -> Dict[str, List]:
    #     """Database of institutions and campuses/location"""
    #     return [
    #         {
    #             "institution_name": "conestoga college",
    #             "cities": [
    #                 {
    #                     "name": "cambridge",
    #                     "campus_list": [
    #                         "downtown",
    #                         "fountain street"
    #                     ]
    #                 },
    #                 {
    #                     "name": "kitchener",
    #                     "campus_list": [
    #                         "doon",
    #                         "downtown"
    #                     ]
    #                 },
    #                 {
    #                     "name": "brantford",
    #                     "campus_list": []
    #                 },
    #                 {
    #                     "name": "guelph",
    #                     "campus_list": []
    #                 },
    #                 {
    #                     "name": "waterloo",
    #                     "campus_list": []
    #                 },
    #                 {
    #                     "name": "ingersoll",
    #                     "campus_list": []
    #                 },
    #                 {
    #                     "name": "stratford",
    #                     "campus_list": []
    #                 }
    #             ]
    #         },
    #         {
    #             "institution_name": "university of waterloo",
    #             "cities": [
    #                 {
    #                     "name": "cambridge",
    #                     "campus_list": []
    #                 },
    #                 {
    #                     "name": "kitchener",
    #                     "campus_list": []
    #                 },
    #                 {
    #                     "name": "stratford",
    #                     "campus_list": []
    #                 }
    #             ]
    #         },
    #         {
    #             "institution_name": "university of guelph",
    #             "cities": [
    #                 {
    #                     "name": "guelph",
    #                     "campus_list": []
    #                 },
    #                 {
    #                     "name": "toronto",
    #                     "campus_list": []
    #                 },
    #                 {
    #                     "name": "ridgetown",
    #                     "campus_list": []
    #                 }
    #             ]
    #         },
    #         {
    #             "institution_name": "wilfred laurier university",
    #             "cities": [
    #                 {
    #                     "name": "brantford",
    #                     "campus_list": []
    #                 },
    #                 {
    #                     "name": "waterloo",
    #                     "campus_list": []
    #                 }
    #             ]
    #         }
    #     ]

    def validate_ORG(self,
                     slot_value: Text,
                     dispatcher: CollectingDispatcher,
                     tracker: Tracker,
                     domain: Dict[Text, Any]) -> Optional[Text]:
        """Validate Educational ORG/Institutes"""
        print("inside validate_ORG action" + tracker.get_slot("ORG"))
        if slot_value.lower() in self.institutions_db():
            return {"ORG": slot_value}
        else:
            dispatcher.utter_message(
                template='utter_institute_not_supported')
            return {"ORG": None}


class ActionSubmitAdmissionsQuery(Action):
    def name(self) -> Text:
        return "action_admissions_query_submit"

    def run(self, dispatcher, tracker: Tracker, domain: "DomainDict") -> List[Dict[Text, Any]]:
        print("inside submission action" + tracker.get_slot("ORG"))
        slots = {
            "ORG": None,
            "GPE": None
        }
        if tracker.get_slot("ORG") is not None:
            dispatcher.utter_message(
                template="utter_test_admissions_query_success", GPE=tracker.get_slot("GPE"), ORG=tracker.get_slot("ORG"))
            return [SlotSet(slot, value) for slot, value in slots.items()]
            # return [SlotSet("ORG", None)]
        return [SlotSet("requested_slot", "ORG")]
