from pynwn.file.gff import Gff, make_gff_property, make_gff_locstring_property
from pynwn.file.gff import GffInstance

from pynwn.scripts import *
from pynwn.vars import *

__all__ = ['Encounter',
           'EncounterInstance',
           'EncounterCreature']

class EncounterCreature(object):
    def __init__(self, gff, parent_obj):
        self.gff = gff
        self.parent_obj = parent_obj
        self.is_instance = True

    def stage(self):
        """Stages changes to the encounter creature instances parent object.
        """        
        self.parent_obj.stage()

ENC_CRE_TABLE = {
    'appearance' : ('Appearance', 'Appearance'),
    'cr'         : ('CR', 'Challenge rating'),
    'resref'     : ('ResRef', 'Resref'),
    'unique'     : ('SingleSpawn', 'Unique spawn.')
}

for key, val in ENC_CRE_TABLE.iteritems():
    setattr(EncounterCreature, key, make_gff_property('gff', val))

TRANSLATION_TABLE = {
    'tag'              : ('Tag', "Tag."),
    'resref'           : ('TemplateResRef', "Resref."),
    'active'           : ('Active', "Active flag."),
    'difficulty'       : ('Difficulty', "Difficulty."),
    'difficulty_index' : ('DifficultyIndex', "Difficulty Index."),
    'faction'          : ('Faction', "Faction ID."),
    'max_creatures'    : ('MaxCreatures', "Maximum creatures."),
    'player_only'      : ('PlayerOnly', "Triggered by player only."),
    'rec_creatures'    : ('RecCreatures', "rec_creatures."),
    'reset'            : ('Reset', "Resets flag."),
    'reset_time'       : ('ResetTime', "Reset time."),
    'respawns'         : ('Respawns', "Respawns."),
    'spawn_option'     : ('SpawnOption', "Spawn option."),
    'palette_id'       : ('PaletteID', "Palette ID."),
    'comment'          : ('Comment', "Comment."),
}

LOCSTRING_TABLE = {
    'name'        : ('LocalizedName', "Localized name."),
}

class Encounter(NWObjectVarable):
    def __init__(self, resref, container, instance=False):
        self._scripts = None
        self._vars = None

        self.is_instance = instance
        if not instance:
            if resref[-4:] != '.ute':
                resref = resref+'.ute'

            if container.has_file(resref):
                self.gff = container[resref]
                self.gff = Gff(self.gff)
            else:
                raise ValueError("Container does not contain: %s" % resref)
        else:
            self.gff = resref

        NWObjectVarable.__init__(self, self.gff)

    @property
    def scripts(self):
        """Scripts. Responts to script events:

        * Event.ENTER
        * Event.EXIT
        * Event.EXHAUSTED
        * Event.HEARTBEAT
        * Event.USER_DEFINED

        """
        if self._scripts: return self._scripts

        lbls = {}
        lbls[Event.ENTER] = 'OnEntered'
        lbls[Event.EXIT] = 'OnExit'
        lbls[Event.EXHAUSTED] = 'OnExhausted'
        lbls[Event.HEARTBEAT] = 'OnHeartbeat'
        lbls[Event.USER_DEFINED] = 'OnUserDefined'

        self._scripts = NWObjectScripts(self.gff, lbls)

        return self._scripts

    @property
    def creatures(self):
        """Creatures in the encounter.

        :returns: List of EncounterCreature objects.
        """
        result = []
        i = 0
        for p in self.gff['CreatureList']:
            gff_inst = GffInstance(self.gff, 'CreatureList', i)
            st_inst  = EncounterCreature(gff_inst, self)
            result.append(st_inst)
            i += 1

        return result

class EncounterInstance(Encounter):
    """A encounter instance is one placed in an area in the toolset.
    As such it's values are derived from its parent GFF structure.
    """
    def __init__(self, gff, parent_obj):
        Encounter.__init__(self, gff, None, True)
        self.is_instance = True
        self.parent_obj = parent_obj

    def stage(self):
        """Stages changes to the encounter instances parent object.
        """
        self.parent_obj.stage()

for key, val in TRANSLATION_TABLE.iteritems():
    setattr(Encounter, key, make_gff_property('gff', val))

for key, val in LOCSTRING_TABLE.iteritems():
    getter, setter = make_gff_locstring_property('gff', val)
    setattr(getter, '__doc__', val[1])
    setattr(setter, '__doc__', val[1])
    setattr(Encounter, 'get_'+key, getter)
    setattr(Encounter, 'set_'+key, setter)