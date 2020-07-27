# -*- coding: utf-8 -*-

from copy import deepcopy
from Products.MeetingCommunes.profiles.testing import import_data as mc_import_data
from Products.PloneMeeting.profiles import UserDescriptor


data = deepcopy(mc_import_data.data)

# Users and groups -------------------------------------------------------------

pmManager = UserDescriptor(
    "pmManager", [], email="pmmanager@plonemeeting.org", fullname="M. PMManager"
)
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
pmReviewer1 = UserDescriptor("pmReviewer1", [])
pmServiceHead1 = UserDescriptor("pmServiceHead1", [])
pmOfficeManager1 = UserDescriptor("pmOfficeManager1", [])
pmDivisionHead1 = UserDescriptor("pmDivisionHead1", [])
pmDirector1 = UserDescriptor("pmDirector1", [])
pmReviewerLevel1 = UserDescriptor(
    "pmReviewerLevel1",
    [],
    email="pmreviewerlevel1@plonemeeting.org",
    fullname="M. PMReviewer Level One",
)
pmCreator2 = UserDescriptor("pmCreator2", [])
pmReviewer2 = UserDescriptor("pmReviewer2", [])
pmReviewerLevel2 = UserDescriptor(
    "pmReviewerLevel2",
    [],
    email="pmreviewerlevel2@plonemeeting.org",
    fullname="M. PMReviewer Level Two",
)
pmAdviser1 = UserDescriptor("pmAdviser1", [])
voter1 = UserDescriptor("voter1", [], fullname="M. Voter One")
voter2 = UserDescriptor("voter2", [], fullname="M. Voter Two")


developers = data.orgs[0]
developers.creators.append(pmCreator1)
developers.creators.append(pmCreator1b)
developers.creators.append(pmManager)
developers.observers.append(pmObserver1)
developers.observers.append(pmReviewer1)
developers.observers.append(pmManager)
developers.advisers.append(pmAdviser1)
developers.advisers.append(pmManager)
developers.serviceheads.append(pmServiceHead1)
developers.serviceheads.append(pmManager)
developers.officemanagers.append(pmOfficeManager1)
developers.officemanagers.append(pmManager)
developers.divisionheads.append(pmDivisionHead1)
developers.divisionheads.append(pmManager)
developers.reviewers.append(pmDirector1)
developers.reviewers.append(pmReviewer1)
developers.reviewers.append(pmManager)
developers.budgetimpactreviewers.append(pmManager)
developers.extraordinarybudget.append(pmManager)

setattr(developers, "signatures", "developers signatures")
setattr(developers, "echevinServices", "developers")

vendors = data.orgs[1]
vendors.creators.append(pmCreator2)
vendors.reviewers.append(pmReviewer2)
vendors.observers.append(pmReviewer2)
vendors.advisers.append(pmReviewer2)
vendors.advisers.append(pmManager)
setattr(vendors, "signatures", "")

# Meeting configurations -------------------------------------------------------
# Meeting configurations -------------------------------------------------------
# college
collegeMeeting = deepcopy(mc_import_data.collegeMeeting)
collegeMeeting.meetingManagers = [
    "pmManager",
]
collegeMeeting.certifiedSignatures = []
collegeMeeting.shortName = "College"
collegeMeeting.usedItemAttributes = (
    "toDiscuss",
    "associatedGroups",
    "itemIsSigned",
)
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
collegeMeeting.selectableCopyGroups = [
    developers.getIdSuffixed("reviewers"),
    vendors.getIdSuffixed("reviewers"),
]


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
councilMeeting.recordItemHistoryStates = []
councilMeeting.maxShownMeetings = 5
councilMeeting.maxDaysDecisions = 60
councilMeeting.meetingAppDefaultView = "searchallitems"
councilMeeting.usedItemAttributes = (
    "toDiscuss",
    "associatedGroups",
    "itemIsSigned",
)
councilMeeting.insertingMethodsOnAddItem = (
    {"insertingMethod": "on_categories", "reverse": "0"},
)
councilMeeting.useGroupsAsCategories = False
councilMeeting.useAdvices = False
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
