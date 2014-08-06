# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('PloneMeeting')

from Acquisition import aq_base

from Products.PloneMeeting.profiles import MeetingFileTypeDescriptor
from Products.PloneMeeting.migrations import Migrator
from plone.app.workflow.remap import remap_workflow
from Products.PloneMeeting.model.adaptations import performWorkflowAdaptations


# The migration class ----------------------------------------------------------
class Migrate_To_3_2_0(Migrator):

    def _addDefaultAdviceAnnexesFileTypes(self):
        '''Add some default MeetingFileType relatedTo 'advice' so we can add
           annexes on advices.'''
        logger.info('Addind default MeetingFileType relatedTo \'advice\'...')
        mfts = []
        mfts.append(MeetingFileTypeDescriptor(id='annexeAvis',
                                              title=u'Annexe à un avis',
                                              theIcon='attach.png',
                                              predefinedTitle='',
                                              relatedTo='advice',
                                              active=True))
        mfts.append(MeetingFileTypeDescriptor(id='annexeAvisLegal',
                                              title=u'Extrait article de loi',
                                              theIcon='legalAdvice.png',
                                              predefinedTitle='',
                                              relatedTo='advice',
                                              active=True))
        # find theIcon path so we can give it to MeetingConfig.addFileType
        mcProfilePath = [profile for profile in self.context.listProfileInfo() if 'id' in profile
                         and profile['id'] == u'Products.MeetingMons:default'][0]['path']
        # the icon are located in the example_fr/images folder
        mcProfilePath = mcProfilePath.replace('profiles/default', 'profiles/mons')
        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            for mft in mfts:
                if not hasattr(aq_base(cfg.meetingfiletypes), mft.id):
                    cfg.addFileType(mft, source=mcProfilePath)
        logger.info('Done.')

    def _transferMotivationField(self):
        '''Replace detailedDescription who used for Motivations by real motivation field
        '''
        brains = self.portal.portal_catalog(meta_type=('MeetingItem'))
        logger.info('Updating Motivation field for %s MeetingItem objects...' % len(brains))
        for brain in brains:
            obj = brain.getObject()
            if not obj.getMotivation():
                obj.setMotivation(obj.getDetailedDescription())
                obj.setDetailedDescription('<p></p>')
                obj.reindexObject()
        logger.info('Done.')

    def _mapPublishedMeetingInDecisionsPublished(self):
        ''' replace Published state for Meeting by activating Published wf adaptation'''
        configs = ('meeting-config-college', 'meeting-config-bp', 'meeting-config-cas',)
        for config in configs:
            conf = getattr(self.portal.portal_plonemeeting, config, None)
            if conf:
                conf.setWorkflowAdaptations(['hide_decisions_when_under_writing', ])
                performWorkflowAdaptations(self.portal, conf, logger)
                type_ids = (conf.getMeetingTypeName(),)
                chain = ('meetingcollegemons_workflow',)
                state_map = {'published': 'decisions_published'}
                logger.info('Remapping meeting workflow')
                remap_workflow(self.portal, type_ids=type_ids, chain=chain, state_map=state_map)
        logger.info('Done.')

    def run(self):
        logger.info('Migrating to MeetingMons 3.2.0...')
        self._addDefaultAdviceAnnexesFileTypes()
        self._transferMotivationField()
        self._mapPublishedMeetingInDecisionsPublished()
        # reinstall so skins and so on are correct
        self.reinstall(profiles=[u'profile-Products.MeetingMons:default', ])
        self.finish()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Add some default MeetingFileType relatedTo 'advice' so we can add annexes on advices.
    '''
    Migrate_To_3_2_0(context).run()
# ------------------------------------------------------------------------------
