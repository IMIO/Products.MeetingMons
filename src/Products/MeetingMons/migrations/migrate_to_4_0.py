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
    '''This migration function:

       1) Execute step3 of Products.PloneMeeting migration profile.
       2) Clean CDLD attributes;
       3) Add an annex type for Meetings;
       4) Remove useless workflows;
       5) Migrate positive decided states.
    '''
    migrator = Migrate_To_4_0(context)
    migrator.run(step=3)
    migrator.finish()
