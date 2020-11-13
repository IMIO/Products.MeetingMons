# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 by Imio.be
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#


from Products.MeetingCommunes.tests.helpers import MeetingCommunesTestingHelpers


class MeetingMonsTestingHelpers(MeetingCommunesTestingHelpers):
    """Stub class that provides some helper methods about testing."""

    TRANSITIONS_FOR_PROPOSING_ITEM_FIRST_LEVEL_1 = TRANSITIONS_FOR_PROPOSING_ITEM_FIRST_LEVEL_2 = (
        "proposeToServiceHead",
        "proposeToOfficeManager",
        "proposeToDivisionHead",
        "proposeToDirector",
    )
    TRANSITIONS_FOR_PROPOSING_ITEM_1 = TRANSITIONS_FOR_PROPOSING_ITEM_2 = (
        "proposeToServiceHead",
        "proposeToOfficeManager",
        "proposeToDivisionHead",
        "proposeToDirector",
    )
    TRANSITIONS_FOR_PRESENTING_ITEM_1 = TRANSITIONS_FOR_PRESENTING_ITEM_2 = (
        "proposeToServiceHead",
        "proposeToOfficeManager",
        "proposeToDivisionHead",
        "proposeToDirector",
        "validate",
        "present",
    )
    TRANSITIONS_FOR_PUBLISHING_MEETING_1 = TRANSITIONS_FOR_PUBLISHING_MEETING_2 = (
        "freeze",
    )
    TRANSITIONS_FOR_FREEZING_MEETING_1 = TRANSITIONS_FOR_FREEZING_MEETING_2 = (
        "freeze",
    )
    TRANSITIONS_FOR_DECIDING_MEETING_1 = (
        "freeze",
        "decide",
    )
    TRANSITIONS_FOR_DECIDING_MEETING_2 = (
        "freeze",
        "decide",
    )
    TRANSITIONS_FOR_CLOSING_MEETING_1 = TRANSITIONS_FOR_CLOSING_MEETING_2 = (
        "freeze",
        "decide",
        "close",
    )
    TRANSITIONS_FOR_ACCEPTING_ITEMS_1 = (
        "freeze",
        "decide",
    )
    TRANSITIONS_FOR_ACCEPTING_ITEMS_2 = (
        "freeze",
        "decide",
    )

    WF_ITEM_STATE_NAME_MAPPINGS_1 = {
        "itemcreated": "itemcreated",
        "proposed_first_level": "proposed_to_director",
        "proposed": "proposed_to_director",
        "validated": "validated",
        "presented": "presented",
        "itemfrozen": "itemfrozen",
    }
    WF_ITEM_STATE_NAME_MAPPINGS_2 = {
        "itemcreated": "itemcreated",
        "proposed_first_level": "proposed_to_director",
        "proposed": "proposed_to_director",
        "validated": "validated",
        "presented": "presented",
        "itemfrozen": "itemfrozen",
    }

    BACK_TO_WF_PATH_1 = BACK_TO_WF_PATH_2 = {
        # Meeting
        "created": ("backToDecided", "backToFrozen", "backToCreated",),
        # MeetingItem
        "itemcreated": (
            "backToItemFrozen",
            "backToPresented",
            "backToValidated",
            "backToPreValidated",
            "backToProposedToDirector",
            "backToProposedToDivisionHead",
            "backToProposedToOfficeManager",
            "backToProposedToServiceHead",
            "backToItemCreated",
        ),
        "proposed_to_servicehead": (
            "backToItemFrozen",
            "backToPresented",
            "backToValidated",
            "backToPreValidated",
            "backToProposedToDirector",
            "backToProposedToDivisionHead",
            "backToProposedToOfficeManager",
            "backToProposedToServiceHead",
        ),
        "proposed_to_officemanager": (
            "backToItemFrozen",
            "backToPresented",
            "backToValidated",
            "backToPreValidated",
            "backToProposedToDirector",
            "backToProposedToDivisionHead",
            "backToProposedToOfficeManager",
        ),
        "proposed_to_divisionhead": (
            "backToItemFrozen",
            "backToPresented",
            "backToValidated",
            "backToPreValidated",
            "backToProposedToDirector",
            "backToProposedToDivisionHead",
        ),
        "proposed_to_director": (
            "backToItemFrozen",
            "backToPresented",
            "backToValidated",
            "backToPreValidated",
            "backToProposedToDirector",
        ),
        "validated": ("backToItemFrozen", "backToPresented", "backToValidated",),
        "presented": ("backToItemFrozen", "backToPresented",),
    }
    # in which state an item must be after an particular meeting transition?
    ITEM_WF_STATE_AFTER_MEETING_TRANSITION = {
        "publish_decisions": "accepted",
        "close": "accepted",
    }

    TRANSITIONS_FOR_ACCEPTING_ITEMS_MEETING_1 = (
        TRANSITIONS_FOR_ACCEPTING_ITEMS_MEETING_2
    ) = (
        "freeze",
        "decide",
    )

    WF_ITEM_TRANSITION_NAME_MAPPINGS_1 = {
        "backToItemCreated": "backToItemCreated",
        "backToProposed": "backToProposedToDirector",
    }
    WF_ITEM_TRANSITION_NAME_MAPPINGS_2 = {
        "backToItemCreated": "backToItemCreated",
        "backToProposed": "backToProposedToDirector",
    }
