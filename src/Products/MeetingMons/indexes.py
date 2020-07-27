from imio.history.interfaces import IImioHistory
from plone.indexer import indexer
from Products.PloneMeeting.interfaces import IMeetingItem
from imio.history.utils import getLastWFAction as getLastEvent
from zope.component import getAdapter

states_before_validated = ('itemcreated',
                           'proposed_to_servicehead',
                           'proposed_to_officemanager',
                           'proposed_to_divisionhead',
                           'proposed_to_director')


@indexer(IMeetingItem)
def toCorrect(obj):
    """
      Indexes the toCorrect on the selected MeetingItem
    """
    res = obj.queryState() in states_before_validated \
          and getLastEvent(obj, 'validate')
    return res


@indexer(IMeetingItem)
def corrected(obj):
    """
      Indexes the corrected items MeetingItem if it is validated but not for the 1st time
    """
    res = False
    if obj.queryState() == 'validated':
        adapter = getAdapter(obj, IImioHistory, 'workflow')
        history = adapter.getHistory(obj, checkMayView=False, history_types=['workflow'])
        if history[-1]['action'] == 'validate':
            validation_count = 0
            i = 0
            while (i) < len(history):
                if history[i]['action'] == 'validate':
                    validation_count += 1
                    if validation_count > 1:
                        res = True
                        break
                i += 1
    return res
