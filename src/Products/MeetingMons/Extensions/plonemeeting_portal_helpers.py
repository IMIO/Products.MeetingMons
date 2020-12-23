# -*- coding: utf-8 -*-

import logging
from collections import OrderedDict

from Products.ZCatalog.ProgressHandler import ZLogHandler
from collective.contact.plonegroup.config import ORGANIZATIONS_REGISTRY
from collective.contact.plonegroup.utils import get_own_organization
from Products.PloneMeeting.utils import org_id_to_uid
from plone import api

logger = logging.getLogger("MeetingMons")


def migrate_field(meeting_config_id):
    migrator = MigrateCategoriesToGroupsInCharge(meeting_config_id)
    migrator.run()


class MigrateCategoriesToGroupsInCharge:
    def __init__(self, meeting_config_id):
        self.meeting_config_id = meeting_config_id

    def _migrate_categories_to_groups_in_charge_field(self):
        logger.info("Migrating Category to Groups in charge field")
        catalog = api.portal.get_tool("portal_catalog")
        own_org = get_own_organization()

        # First we create the appropriate groupsInCharge
        logger.info("Adapting MeetingConfig...")
        cfg = catalog(portal_type="MeetingConfig", id=self.meeting_config_id)[0].getObject()
        categories = cfg.categories
        for cat_id, category in categories.contentItems():
            if cat_id not in own_org.objectIds():
                data = {"id": cat_id, "title": category.Title(), "description": category.Description()}
                api.content.create(container=own_org, type="organization", **data)
            new_org_uid = org_id_to_uid(cat_id)

            enabled_plonegroup_org_uids = api.portal.get_registry_record(ORGANIZATIONS_REGISTRY)
            if new_org_uid not in enabled_plonegroup_org_uids:
                api.portal.set_registry_record(ORGANIZATIONS_REGISTRY, enabled_plonegroup_org_uids + [new_org_uid])

            ordered_group_in_charge_uids = cfg.getOrderedGroupsInCharge()
            if new_org_uid not in ordered_group_in_charge_uids:
                cfg.setOrderedGroupsInCharge(ordered_group_in_charge_uids + (new_org_uid,))

            category.enabled = False

        # Next we migrate the category to groupsInCharge on MeetingItems
        brains = catalog(
            portal_type=(
                cfg.getItemTypeName(),
                cfg.getItemTypeName(configType="MeetingItemRecurring"),
                cfg.getItemTypeName(configType="MeetingItemTemplate"),
            )
        )
        pghandler = ZLogHandler(steps=1000)
        pghandler.init("Adapting items...", len(brains))
        for i, brain in enumerate(brains):
            pghandler.report(i)
            item = brain.getObject()
            if item.getCategory() != u"_none_":
                item.setGroupsInCharge([org_id_to_uid(item.getCategory())])
                item.setCategory(None)
                item.reindexObject(idxs=["getGroupsInCharge", "getCategory"])
        pghandler.finish()

        logger.info("Done migrating Categories to Groups in charge field")

    def run(self):
        self._migrate_categories_to_groups_in_charge_field()


def add_portal_categories(meeting_config_id="meeting-config-council"):
    CATEGORIES = OrderedDict(
        [
            ("administration", "Administration générale"),
            ("immo", "Affaires immobilières"),
            ("espaces-publics", "Aménagement des espaces publics"),
            ("batiments-communaux", "Bâtiments communaux"),
            ("animaux", "Bien-être animal"),
            ("communication", "Communication & Relations extérieures"),
            ("cultes", "Cultes"),
            ("culture", "Culture & Folklore"),
            ("economie", "Développement économique & commercial"),
            ("enseignement", "Enseignement"),
            ("population", "État civil & Population"),
            ("finances", "Finances"),
            ("informatique", "Informatique"),
            ("interculturalite", "Interculturalité & Égalité"),
            ("jeunesse", "Jeunesse"),
            ("logement", "Logement & Énergie"),
            ("mobilite", "Mobilité"),
            ("quartier", "Participation relation avec les quartiers"),
            ("patrimoine", "Patrimoine"),
            ("enfance", "Petite enfance"),
            ("politique", "Politique générale"),
            ("environnement", "Propreté & Environnement"),
            ("sante", "Santé"),
            ("securite", "Sécurité & Prévention"),
            ("social", "Services sociaux"),
            ("sport", "Sport"),
            ("tourisme", "Tourisme"),
            ("urbanisme", "Urbanisme & Aménagement du territoire"),
            ("police", "Zone de police"),
        ]
    )
    logger.info("Adding global categories...")
    catalog = api.portal.get_tool("portal_catalog")
    cfg = catalog(portal_type="MeetingConfig", id=meeting_config_id)[0].getObject()
    categories = cfg.categories
    for cat_id, cat_title in CATEGORIES.items():
        if cat_id not in categories.objectIds():
            data = {
                "id": cat_id,
                "title": cat_title,
            }
            api.content.create(container=categories, type="meetingcategory", **data)
