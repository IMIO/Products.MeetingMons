# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingMons')

from plone import api

from Products.MeetingMons.profiles.mons.import_data import annexeSeance
from Products.PloneMeeting.migrations.migrate_to_4_0 import Migrate_To_4_0 as PMMigrate_To_4_0


# The migration class ----------------------------------------------------------
class Migrate_To_4_0(PMMigrate_To_4_0):

    wfs_to_delete = []

    def _cleanCDLD(self):
        """We removed things related to 'CDLD' finance advice, so:
           - remove the 'cdld-document-generate' from document_actions;
           - remove the MeetingConfig.CdldProposingGroup attribute.
        """
        logger.info('Removing CDLD related things...')
        doc_actions = self.portal.portal_actions.document_actions
        # remove the action from document_actions
        if 'cdld-document-generate' in doc_actions:
            doc_actions.manage_delObjects(ids=['cdld-document-generate', ])
        # clean the MeetingConfigs
        for cfg in self.tool.objectValues('MeetingConfig'):
            if hasattr(cfg, 'cdldProposingGroup'):
                delattr(cfg, 'cdldProposingGroup')
        logger.info('Done.')

    def _migrateItemPositiveDecidedStates(self):
        """Before, the states in which an item was auto sent to
           selected other meetingConfig was defined in a method
           'itemPositiveDecidedStates' now it is stored in MeetingConfig.itemAutoSentToOtherMCStates.
           We store these states in the MeetingConfig.itemPositiveDecidedStates, it is used
           to display the 'sent from' leading icon on items sent from another MeetingConfig."""
        logger.info('Defining values for MeetingConfig.itemAutoSentToOtherMCStates...')
        for cfg in self.tool.objectValues('MeetingConfig'):
            cfg.setItemAutoSentToOtherMCStates(('accepted', 'accepted_but_modified', ))
            cfg.setItemPositiveDecidedStates(('accepted', 'accepted_but_modified', ))
        logger.info('Done.')

    def _after_reinstall(self):
        """Use that hook that is called just after the profile has been reinstalled by
           PloneMeeting, this way, we may launch some steps before PloneMeeting ones.
           Here we will update used workflows before letting PM do his job."""
        logger.info('after_reinstall ...')
        PMMigrate_To_4_0._after_reinstall(self)
        logger.info('Done.')

    def _addSampleAnnexTypeForMeetings(self):
        """Add a sample annexType for Meetings now that
           annexes may be added to meetings."""
        logger.info('Adding sample annexType in meeting_annexes...')
        for cfg in self.tool.objectValues('MeetingConfig'):
            if not cfg.annexes_types.meeting_annexes.objectIds():
                source = self.ps.getProfileInfo(
                    self.profile_name)['path'].replace('/default', '/mons')
                cfg.addAnnexType(annexeSeance, source)
        logger.info('Done.')

    def _deleteUselessWorkflows(self):
        """Finally, remove useless workflows."""
        logger.info('Removing useless workflows...')
        if self.wfs_to_delete:
            wfTool = api.portal.get_tool('portal_workflow')
            wfTool.manage_delObjects(self.wfs_to_delete)
        logger.info('Done.')

    def _updateConfig(self):
        logger.info('Updating config ...')

        # remove custom buggy skin
        if 'imioapps_properties' in  self.portal.portal_skins.custom.objectIds():
            self.portal.portal_skins.custom.manage_delObjects(ids=['imioapps_properties'])

        for cfg in self.tool.objectValues('MeetingConfig'):
            wfAdaptations = list(cfg.getWorkflowAdaptations())
            wfAdaptations.append('postpone_next_meeting')
            cfg.setWorkflowAdaptations(tuple(wfAdaptations))

            itemAttributes = ['budgetInfos', 'motivation', 'observations', 'toDiscuss', 'itemAssembly', 'privacy']

            itemColumns = ['Creator', 'CreationDate', 'ModificationDate', 'review_state', 'getCategory',
                           'proposing_group_acronym', 'advices', 'toDiscuss', 'linkedMeetingDate', 'getPreferredMeetingDate']

            availableItemColumns = ['Creator', 'CreationDate', 'ModificationDate', 'getCategory',
                           'proposing_group_acronym', 'advices', 'toDiscuss',
                           'getPreferredMeetingDate']

            meetingItemColumn = ['item_reference', 'Creator', 'ModificationDate', 'review_state', 'getCategory',
                                 'proposing_group_acronym', 'advices', 'toDiscuss', 'actions']

            itemColumnsFilters= ['c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'c10', 'c11', 'c13', 'c14', 'c15', 'c16', 'c19']

            meetingItemFilter = ['c4', 'c5', 'c6', 'c7', 'c8', 'c11', 'c13', 'c14', 'c16', 'c19']

            if cfg.getId() == 'meeting-config-college':
                itemAttributes.remove('privacy')
                itemColumnsFilters.remove('c19')
            elif cfg.getId() == 'meeting-config-council':
                itemAttributes.remove('toDiscuss')
                itemColumns.remove('toDiscuss')
                availableItemColumns.remove('toDiscuss')
                meetingItemColumn.remove('toDiscuss')
                itemColumnsFilters.remove('c16')
            else:
                itemAttributes.remove('toDiscuss')
                itemAttributes.remove('privacy')

                meetingItemColumn.remove('toDiscuss')
                meetingItemColumn.remove('getCategory')
                itemColumns.remove('toDiscuss')
                availableItemColumns.remove('toDiscuss')
                itemColumns.remove('getCategory')
                availableItemColumns.remove('getCategory')

                itemColumnsFilters.remove('c5')
                itemColumnsFilters.remove('c19')
                meetingItemFilter.remove('c5')
                meetingItemFilter.remove('c19')

                if cfg.getId() == 'meeting-config-cas':
                    itemColumnsFilters.remove('c16')
                elif cfg.getId() == 'meeting-config-bp':
                    pass

            # item
            cfg.setUsedItemAttributes(tuple(itemAttributes))

            # meeting
            cfg.setUsedMeetingAttributes(('startDate', 'endDate', 'signatures', 'assembly', 'assemblyExcused',
                                          'assemblyAbsents', 'place', 'observations',))
            # dashboard list items
            cfg.setItemColumns(tuple(itemColumns))
            cfg.setDashboardItemsListingsFilters(tuple(itemColumnsFilters))
            cfg.setMaxShownListings('20')

            # dashboard list available items for meeting
            cfg.setAvailableItemsListVisibleColumns(tuple(availableItemColumns))

            cfg.setDashboardMeetingAvailableItemsFilters(tuple(itemColumnsFilters))
            cfg.setMaxShownAvailableItems('40')

            # dashboard list presented items in meeting
            cfg.setItemsListVisibleColumns(tuple(meetingItemColumn))
            cfg.setDashboardMeetingLinkedItemsFilters(tuple(meetingItemFilter))
            cfg.setMaxShownMeetingItems('60')

            cfg.at_post_edit_script()

    def run(self, step=None):
        # change self.profile_name that is reinstalled at the beginning of the PM migration
        self.profile_name = u'profile-Products.MeetingMons:default'

        # call steps from Products.PloneMeeting
        PMMigrate_To_4_0.run(self, step=step)

        if step == 3:
            # now MeetingMons specific steps
            logger.info('Migrating to MeetingMons 4.0...')
            self._cleanCDLD()
            self._migrateItemPositiveDecidedStates()
            self._addSampleAnnexTypeForMeetings()
            self._deleteUselessWorkflows()

        if step == 5:
            self._updateConfig()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Reinstall Products.MeetingMons and execute the Products.PloneMeeting migration;
       2) Clean CDLD attributes;
       3) Add an annex type for Meetings;
       4) Remove useless workflows;
       5) Migrate positive decided states.
    '''
    migrator = Migrate_To_4_0(context)
    migrator.run()
    migrator.finish()


def migrate_step1(context):
    '''This migration function:

       1) Reinstall Products.MeetingMons and execute the Products.PloneMeeting migration.
    '''
    migrator = Migrate_To_4_0(context)
    migrator.run(step=1)
    migrator.finish()


def migrate_step2(context):
    '''This migration function:

       1) Execute step2 of Products.PloneMeeting migration profile (imio.annex).
    '''
    migrator = Migrate_To_4_0(context)
    migrator.run(step=2)
    migrator.finish()


def migrate_step3(context):
    '''
       This migration function:

       1) Execute step3 of Products.PloneMeeting migration profile.
       2) Clean CDLD attributes;
       3) Add an annex type for Meetings;
       4) Remove useless workflows;
       5) Migrate positive decided states.
    '''
    migrator = Migrate_To_4_0(context)
    migrator.run(step=3)
    migrator.finish()


def migrate_step5_customs(context):
    migrator = Migrate_To_4_0(context)
    migrator.run(step=5)
    migrator.finish()
