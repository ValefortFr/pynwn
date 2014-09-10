from pynwn.file.gff import Gff, GffInstance, make_gff_locstring_property
from pynwn.file.gff import make_gff_property

from pynwn.item import RepositoryItem, ItemInstance
from pynwn.scripts import *
from pynwn.vars import *

TRANSLATION_TABLE = {
    'resref'          : ('ResRef', "Resref."),
    'tag'             : ('Tag', "Tag."),
    'mark_up'         : ('MarkUp', "Mark up."),
    'mark_down'       : ('MarkDown', "Mark down."),
    'black_market'    : ('BlackMarket', "Black market flag."),
    'mark_down_bm'    : ('BM_MarkDown', "Blackmarket mark down."),
    'price_id'        : ('IdentifyPrice', "Price to identify item."),
    'price_max_buy'   : ('MaxBuyPrice', "Maximum buy price."),
    'gold'            : ('StoreGold', "Gold."),
    'palette_id'      : ('PaletteID', "Resref."),
    'comment'         : ('Comment', "Comment."),
}

LOCSTRING_TABLE = {
    'name'           : ('LocName', "Localized name."),
    'description'    : ('Description', "Localized unidentified description."),
    'description_id' : ('DescIdentified', "Localized identified description."),
}

class Store(object):
    def __init__(self, resource, instance=False):
        self._scripts = None
        self._vars = None
        self.is_file = False

        self.is_instance = instance
        if not instance:
            if isinstance(resource, str):
                from resource import ContentObject
                co = ContentObject.from_file(resource)
                self.gff = Gff(co)
                self.is_file = True
            else:
                self.container = resource[1]
                self.gff = Gff(resource[0])
        else:
            self.gff = resource


    def stage(self):
        if self.gff.is_loaded():
            self.container.add_to_saves(self.gff)

    @property
    def vars(self):
        """ Variable table """
        if self._vars: return self._vars
        self._vars = NWObjectVarable(self, self.gff)
        return self._vars

    @property
    def script(self):
        """Scripts.  Responds to script events:

        #. Event.OPEN
        #. Event.CLOSE
        """
        if self._scripts: return self._scripts

        lbls = {}
        lbls[Event.OPEN] = 'OnOpenStore'
        lbls[Event.CLOSE] = 'OnStoreClosed'

        self._scripts = NWObjectScripts(self.gff, lbls)

        return self._scripts

    @property
    def will_not_buy(self):
        """Will not buy list.

        :returns: List of baseitem IDs that store will not buy.
        """
        return [i['BaseItem'] for i in self['WillNotBuy']]

    @property
    def will_only_buy(self):
        """Will only buy list.

        :returns: List of baseitem IDs that store will only buy.
        """
        return [i['BaseItem'] for i in self['WillOnlyBuy']]

    @property
    def items(self):
        """Items in inventory.

        :returns: a two dimensional array with the format:
                  [<store page>][<RepositoryItem objects>]
        """
        res = []
        for page in self['StoreList']:
            items = []
            try:
                for p in self.gff['ItemList']:
                    gff_inst = GffInstance(self, self.gff, 'ItemList', i)
                    st_inst  = RepositoryItem(gff_inst)
                    items.append(st_inst)
                    i += 1
            except Exception as e:
                print(e)
                pass

            res.append(items)

        return res

class StoreInstance(Store):
    """A store instance is one placed in an area in the toolset.
    As such it's values are derived from its parent GFF structure.
    """
    def __init__(self, gff, parent_obj):
        Store.__init__(self, gff, True)
        self.is_instance = True
        self.parent_obj = parent_obj

    def stage(self):
        """Stages changes to parent GFF structure.
        """
        self.parent_obj.stage()

    @property
    def items(self):
        """Items in inventory.

        :returns: a two dimensional array with the format:
                  [<store page>][<ItemInstance objects>]
        """
        res = []
        for page in self['StoreList']:
            items = []
            try:
                for p in self.gff['ItemList']:
                    gff_inst = GffInstance(self.parent_obj, self.gff, 'ItemList', i)
                    st_inst  = ItemInstance(gff_inst)
                    items.append(st_inst)
                    i += 1

            except Exception as e:
                print(e)
                pass

            res.append( items )

        return res

for key, val in TRANSLATION_TABLE.iteritems():
    setattr(Store, key, make_gff_property('gff', val))

for key, val in LOCSTRING_TABLE.iteritems():
    getter, setter = make_gff_locstring_property('gff', val)
    setattr(getter, '__doc__', val[1])
    setattr(setter, '__doc__', val[1])
    setattr(Store, 'get_'+key, getter)
    setattr(Store, 'set_'+key, setter)
