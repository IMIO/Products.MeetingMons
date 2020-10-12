# -*- coding: utf-8 -*-

from copy import deepcopy

from Products.PloneMeeting.config import MEETINGREVIEWERS
from Products.PloneMeeting.profiles.testing import import_data as pm_import_data
from Products.MeetingCommunes.profiles.testing import import_data as mc_import_data
from Products.PloneMeeting.profiles import UserDescriptor


data = deepcopy(mc_import_data.data)

# Users and groups -------------------------------------------------------------
pmCreator1 = UserDescriptor(
    "pmCreator1", [], email="pmcreator1@plonemeeting.org", fullname="M. PMCreator One"
)
pmCreator1b = UserDescriptor(
    "pmCreator1b",
    [],
    email="pmcreator1b@plonemeeting.org",
    fullname="M. PMCreator One bee",
)
pmObserver1 = UserDescriptor(
    "pmObserver1",
    [],
    email="pmobserver1@plonemeeting.org",
    fullname="M. PMObserver One",
)
pmServiceHead1 = UserDescriptor("pmServiceHead1", [])
pmOfficeManager1 = UserDescriptor("pmOfficeManager1", [])
pmDivisionHead1 = UserDescriptor("pmDivisionHead1", [])
pmDirector1 = UserDescriptor("pmDirector1", [])
pmCreator2 = UserDescriptor("pmCreator2", [])
pmAdviser1 = UserDescriptor("pmAdviser1", [])
voter1 = UserDescriptor("voter1", [], fullname="M. Voter One")
voter2 = UserDescriptor("voter2", [], fullname="M. Voter Two")


# Meeting configurations -------------------------------------------------------
# Meeting configurations -------------------------------------------------------
# college
collegeMeeting = deepcopy(mc_import_data.collegeMeeting)
collegeMeeting.meetingManagers = [
    "pmManager",
]
collegeMeeting.shortName = "College"
collegeMeeting.maxShownListings = "100"
collegeMeeting.itemWorkflow = "meetingitemcollegemons_workflow"
collegeMeeting.meetingWorkflow = "meetingcollegemons_workflow"
collegeMeeting.itemConditionsInterface = (
    "Products.MeetingMons.interfaces.IMeetingItemCollegeMonsWorkflowConditions"
)
collegeMeeting.itemActionsInterface = (
    "Products.MeetingMons.interfaces.IMeetingItemCollegeMonsWorkflowActions"
)
collegeMeeting.meetingConditionsInterface = (
    "Products.MeetingMons.interfaces.IMeetingCollegeMonsWorkflowConditions"
)
collegeMeeting.meetingActionsInterface = (
    "Products.MeetingMons.interfaces.IMeetingCollegeMonsWorkflowActions"
)
collegeMeeting.transitionsForPresentingAnItem = (
    "proposeToServiceHead",
    "proposeToOfficeManager",
    "proposeToDivisionHead",
    "proposeToDirector",
    "validate",
    "present",
)
collegeMeeting.itemAdviceStates = [
    "proposed_to_director",
]
collegeMeeting.itemAdviceEditStates = ["proposed_to_director", "validated"]
collegeMeeting.itemAdviceViewStates = [
    "presented",
]
collegeMeeting.transitionsReinitializingDelays = ("backToItemCreated",)
collegeMeeting.enforceAdviceMandatoriness = False
collegeMeeting.itemPowerObserversStates = (
    "itemcreated",
    "presented",
    "accepted",
    "delayed",
    "refused",
)
collegeMeeting.itemDecidedStates = [
    "accepted",
    "refused",
    "delayed",
    "accepted_but_modified",
    "pre_accepted",
]
collegeMeeting.workflowAdaptations = []
collegeMeeting.insertingMethodsOnAddItem = (
    {"insertingMethod": "on_proposing_groups", "reverse": "0"},
)
collegeMeeting.useGroupsAsCategories = True
collegeMeeting.meetingPowerObserversStates = ("frozen", "decided", "closed")
collegeMeeting.useCopies = True

# Conseil communal
councilMeeting = deepcopy(mc_import_data.councilMeeting)
councilMeeting.meetingManagers = [
    "pmManager",
]
councilMeeting.certifiedSignatures = []
councilMeeting.shortName = "Council"
councilMeeting.itemWorkflow = "meetingitemcollegemons_workflow"
councilMeeting.meetingWorkflow = "meetingcollegemons_workflow"
councilMeeting.itemConditionsInterface = (
    "Products.MeetingMons.interfaces.IMeetingItemCollegeMonsWorkflowConditions"
)
councilMeeting.itemActionsInterface = (
    "Products.MeetingMons.interfaces.IMeetingItemCollegeMonsWorkflowActions"
)
councilMeeting.meetingConditionsInterface = (
    "Products.MeetingMons.interfaces.IMeetingCollegeMonsWorkflowConditions"
)
councilMeeting.meetingActionsInterface = (
    "Products.MeetingMons.interfaces.IMeetingCollegeMonsWorkflowActions"
)
councilMeeting.transitionsToConfirm = []
councilMeeting.transitionsForPresentingAnItem = (
    "proposeToServiceHead",
    "proposeToOfficeManager",
    "proposeToDivisionHead",
    "proposeToDirector",
    "validate",
    "present",
)
councilMeeting.itemCopyGroupsStates = ['accepted']
councilMeeting.onMeetingTransitionItemTransitionToTrigger = (
    {"meeting_transition": "freeze", "item_transition": "itemfreeze"},
    {"meeting_transition": "decide", "item_transition": "itemfreeze"},
    {"meeting_transition": "publish_decisions", "item_transition": "itemfreeze"},
    {"meeting_transition": "publish_decisions", "item_transition": "accept"},
    {"meeting_transition": "close", "item_transition": "itemfreeze"},
    {"meeting_transition": "close", "item_transition": "accept"},
    {"meeting_transition": "backToCreated", "item_transition": "backToPresented"},
)

councilMeeting.meetingTopicStates = ("created", "frozen")
councilMeeting.decisionTopicStates = ("decided", "closed")
councilMeeting.itemAdviceStates = ("validated",)
councilMeeting.itemAdviceStates = [
    "proposed_to_director",
]
councilMeeting.itemAdviceEditStates = ["proposed_to_director", "validated"]
councilMeeting.itemAdviceViewStates = [
    "presented",
]
councilMeeting.transitionsReinitializingDelays = "backToItemCreated"
councilMeeting.enforceAdviceMandatoriness = False
councilMeeting.itemDecidedStates = [
    "accepted",
    "refused",
    "delayed",
    "accepted_but_modified",
    "pre_accepted",
]
councilMeeting.itemPowerObserversStates = collegeMeeting.itemPowerObserversStates
councilMeeting.meetingPowerObserversStates = collegeMeeting.meetingPowerObserversStates

data.meetingConfigs = (collegeMeeting, councilMeeting)
