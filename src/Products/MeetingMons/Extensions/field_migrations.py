# -*- coding: utf-8 -*-

import logging

from Products.ZCatalog.ProgressHandler import ZLogHandler
from collective.contact.plonegroup.config import ORGANIZATIONS_REGISTRY
from collective.contact.plonegroup.utils import get_own_organization
from Products.PloneMeeting.utils import org_id_to_uid
from plone import api


def migrate_field(meeting_config_id="meeting-config-college"):
    migrator = MigrateCategoriesToGroupsInCharge(meeting_config_id)
    migrator.run()


logger = logging.getLogger('MeetingMons')


# The migration class ----------------------------------------------------------
class MigrateCategoriesToGroupsInCharge:

    def __init__(self, meeting_config_id):
        self.meeting_config_id = meeting_config_id

    def _migrate_categories_to_groups_in_charge_field(self):
        logger.info('Migrating Category to Groups in charge field')
        catalog = api.portal.get_tool('portal_catalog')
        tool = api.portal.get_tool('portal_plonemeeting')
        own_org = get_own_organization()
        logger.info("Adapting MeetingConfig...")
        cfg = catalog(portal_type="MeetingConfig", id=self.meeting_config_id)[0].getObject()

        categories = cfg.categories
        for cat_id, category in categories.contentItems():

            if cat_id not in own_org:
                data = {
                    'id': cat_id,
                    'title': category.Title(),
                    'description': category.Description()
                }
                api.content.create(container=own_org, type='organization', **data)
            new_org_uid = org_id_to_uid(cat_id)

            enabled_plonegroup_org_uids = api.portal.get_registry_record(ORGANIZATIONS_REGISTRY)
            if new_org_uid not in enabled_plonegroup_org_uids:
                api.portal.set_registry_record(ORGANIZATIONS_REGISTRY, enabled_plonegroup_org_uids + [new_org_uid])

            ordered_group_in_charge_uids = cfg.getOrderedGroupsInCharge()
            if new_org_uid not in ordered_group_in_charge_uids:
                cfg.setOrderedGroupsInCharge(
                    ordered_group_in_charge_uids + (new_org_uid,)
                )

            category.enabled = False

        brains = catalog(portal_type=cfg.getItemTypeName())
        pghandler = ZLogHandler(steps=1000)
        pghandler.init('Adapting items...', len(brains))
        failed_items = []
        for i, brain in enumerate(brains):
            pghandler.report(i)
            item = brain.getObject()
            try:
                if item.getCategory() != u'_none_':
                    item.setGroupsInCharge([org_id_to_uid(item.getCategory())])
                    item.reindexObject(idxs=["getGroupsInCharge"])
            except:
                failed_items += [item.Title()]
        pghandler.finish()

        if len(failed_items) > 0:
            logger.warning("Following items could not be migrated : " + "\n -".join(failed_items))
        logger.info('Done migrating Categories to Groups in charge field')

    def run(self):
        self._migrate_categories_to_groups_in_charge_field()
