Products.MeetingMons Changelog
==================================

Older versions than 3.0 can be found at http://svn.communesplone.org/svn/communesplone/MeetingMons/tags/
The Products.MeetingMons version must be the same as the Products.PloneMeeting version

4.1.0.2 (2020-10-12)
--------------------

- Fixed tests from testSetup.
  [aduchene]
- Fixed some display issues.
  [aduchene]


4.1.0.1 (2020-09-18)
--------------------

- Migrated HISTORY.txt to CHANGES.rst
- Added Jenkinsfile
- Updated scaffolding (setup.py, README.rst,...)


3.3 (2015-05-08)
----------------

- Adapted workflows to define the icon to use for transitions
- Removed field MeetingConfig.cdldProposingGroup and use the 'indexAdvisers' value
  defined in the 'searchitemswithfinanceadvice' collection to determinate what are
  the finance adviser group ids
- 'getEchevinsForProposingGroup' does also return inactive MeetingGroups so when used
  as a TAL condition in a customAdviser, an inactive MeetingGroup/customAdviser does
  still behaves correctly when updating advices
- Use ToolPloneMeeting.performCustomWFAdaptations to manage our own WFAdaptation
  (override of the 'no_publication' WFAdaptation)
- Adapted tests, keep test... original PM files to overrides original PM tests and
  use testCustom... for every other tests, added a testCustomWorkflow.py
- Now that the same WF may be used in several MeetingConfig in PloneMeeting, removed the
  2 WFs meetingcollege and meetingcouncil and use only one MeetingMons where wfAdaptations
  'no_publication' and 'no_global_observation' are enabled
- Added profile 'financesadvice' to manage advanced finances advice using a particular
  workflow and a specific meetingadvicefinances portal_type
- Adapted profiles to reflect imio.annex integration
- Added new adapter method to ease financial advices management while generating documents
  printFinanceAdvice(self, case)
- Added parameter 'excludedGroupIds' to getPrintableItems and getPrintableItemsByCategory
- MeetingObserverLocal has every View-like permissions in every states
- Adapted default 'deliberation.odt' to no more use global margin and integrate printAllAnnexes


3.3 (2015-02-27)
----------------

- Updated regarding changes in PloneMeeting
- Removed profile 'examples' that loaded examples in english
- Removed dependencies already defined in PloneMeeting's setup.py
- Added parameter MeetingConfig.initItemDecisionIfEmptyOnDecide that let enable/disable
  items decision field initialization when meeting 'decide' transition is triggered
- Added MeetingConfig 'CoDir'
- Field 'MeetingGroup.signatures' was moved to PloneMeeting


3.2.0.1 (2014-03-06)
--------------------

- Updated regarding changes in PloneMeeting
- Moved some translations from the plone domain to the PloneMeeting domain
- Refactored tests regarding changes in PloneMeeting

3.2.0 (2014-02-12)
------------------

- Updated regarding changes in PloneMeeting
- Use getToolByName where necessary


3.1.0 (2013-11-04)
------------------

- Simplified overrides now that PloneMeeting manage this correctly
- Moved 'add_published_state' to PloneMeeting and renamed to 'hide_decisions_when_under_writing'
- Moved 'searchitemstovalidate' topic to PloneMeeting now that PloneMeeting also manage a 'searchitemstoprevalidate' search


3.0.3 (unreleased)
------------------

- An item can be deleted by member only if item's state is created, else it's Manager (only) who be able to remove its.
- Remove state in_waiting_advice (items is change on itemcreated)
- Remove topics in_waiting_advice
- Add check for Budget Impact reviewer : Validate by budget info
- Add Field Default-Motivation
- 3P ling activate with WebServices


3.0.2 (2013-06-21)
------------------

- Removed override of Meeting.mayChangeItemsOrder
- Removed override of meeting_changeitemsorder
- Removed override of browser.async.Discuss.isAsynchToggleEnabled, now enabled by default
- Added missing tests from PloneMeeting
- Corrected bug in printAdvicesInfos leading to UnicodeDecodeError when no advice was asked on an item


3.0.1 (2013-06-07)
------------------

- Added sample of document template with printed annexes
- Added method to ease pritning of assembly with 'category' of assembly members
- Make printing by category as functionnal as printing without category
- Corrected bug while going back to published that could raise a WorkflowException sometimes


3.0 (2013-04-03)
----------------

- Migrated to Plone 4 (use PloneMeeting 3.x, see PloneMeeting's HISTORY.txt for full changes list)


2.1.3 (2012-09-19)
------------------

- Added possibility to give, modify and view an advice on created item
- Added possibility to define a decision of replacement when an item is delayed
- Added new workflow adaptation to add publish state with hidden decision for no meeting-manager
