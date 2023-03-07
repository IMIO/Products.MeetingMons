# -*- coding: utf-8 -*-

from DateTime import DateTime
from Products.MeetingMons.config import MONS_ITEM_WF_VALIDATION_LEVELS
from plone import api
from Products.MeetingCommunes.migrations.migrate_to_4200 import Migrate_To_4200 as MCMigrate_To_4200
import logging

logger = logging.getLogger('MeetingMons')


class Migrate_To_4200(MCMigrate_To_4200):

    def _fixUsedWFs(self):
        """meetingseraing_workflow/meetingitemseraing_workflow do not exist anymore,
           we use meeting_workflow/meetingitem_workflow."""
        logger.info("Adapting 'meetingWorkflow/meetingItemWorkflow' for every MeetingConfigs...")
        for cfg in self.tool.objectValues('MeetingConfig'):
            if cfg.getMeetingWorkflow() in (
                    'meetingcollegemons_workflow',
            ):
                cfg.setMeetingWorkflow('meeting_workflow')
            if cfg.getItemWorkflow() in (
                    'meetingitemcollegemons_workflow',
            ):
                cfg.setItemWorkflow('meetingitem_workflow')
        # delete old unused workflows
        wfs_to_delete = [wfId for wfId in self.wfTool.listWorkflows()
                         if any(x in wfId for x in ('meetingcollegemons_workflow','meetingitemcollegemons_workflow',))]
        if wfs_to_delete:
            self.wfTool.manage_delObjects(wfs_to_delete)
        logger.info('Done.')

    def _get_wh_key(self, itemOrMeeting):
        """Get workflow_history key to use, in case there are several keys, we take the one
           having the last event."""
        keys = itemOrMeeting.workflow_history.keys()
        if len(keys) == 1:
            return keys[0]
        else:
            lastEventDate = DateTime('1950/01/01')
            keyToUse = None
            for key in keys:
                if itemOrMeeting.workflow_history[key][-1]['time'] > lastEventDate:
                    lastEventDate = itemOrMeeting.workflow_history[key][-1]['time']
                    keyToUse = key
            return keyToUse

    def _adaptWFHistoryForItemsAndMeetings(self):
        """We use PM default WFs, no more meeting(item)lalouviere_workflow..."""
        logger.info('Updating WF history items and meetings to use new WF id...')
        catalog = api.portal.get_tool('portal_catalog')
        for cfg in self.tool.objectValues('MeetingConfig'):
            # this will call especially part where we duplicate WF and apply WFAdaptations
            cfg.registerPortalTypes()
            for brain in catalog(portal_type=(cfg.getItemTypeName(), cfg.getMeetingTypeName())):
                itemOrMeeting = brain.getObject()
                itemOrMeetingWFId = self.wfTool.getWorkflowsFor(itemOrMeeting)[0].getId()
                if itemOrMeetingWFId not in itemOrMeeting.workflow_history:
                    wf_history_key = self._get_wh_key(itemOrMeeting)
                    itemOrMeeting.workflow_history[itemOrMeetingWFId] = \
                        tuple(itemOrMeeting.workflow_history[wf_history_key])
                    del itemOrMeeting.workflow_history[wf_history_key]
                    # do this so change is persisted
                    itemOrMeeting.workflow_history = itemOrMeeting.workflow_history
                else:
                    # already migrated
                    break
        logger.info('Done.')

    def _safe_add_WFA(self, wfa, cfg):
        if wfa in cfg.getWorkflowAdaptations():
            return
        cfg.setWorkflowAdaptations((wfa,) + cfg.getWorkflowAdaptations())


    def _doConfigureItemWFValidationLevels(self, cfg):
        """Apply correct itemWFValidationLevels and fix WFAs."""
        stored_itemWFValidationLevels = getattr(cfg, 'itemWFValidationLevels', [])
        if not stored_itemWFValidationLevels:
            cfg.setItemWFValidationLevels(MONS_ITEM_WF_VALIDATION_LEVELS)

        self._safe_add_WFA("accepted_but_modified", cfg)
        self._safe_add_WFA("refused", cfg)
        self._safe_add_WFA("delayed", cfg)
        self._safe_add_WFA("mons_budget_reviewer", cfg)

    def run(self,
            profile_name=u'profile-Products.MeetingMons:default',
            extra_omitted=[]):
        self._fixUsedWFs()
        super(Migrate_To_4200, self).run(extra_omitted=extra_omitted)
        self._adaptWFHistoryForItemsAndMeetings()
        logger.info('Done migrating to MeetingMons 4200...')


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Change MeetingConfig workflows to use meeting_workflow/meetingitem_workflow;
       2) Call PloneMeeting migration to 4200 and 4201;
       3) In _after_reinstall hook, adapt items and meetings workflow_history
          to reflect new defined workflow done in 1);
    '''
    migrator = Migrate_To_4200(context)
    migrator.run()
    migrator.finish()
