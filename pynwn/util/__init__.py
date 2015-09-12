#coding=utf-8
"""
A dictionary difference calculator
Originally posted as:
http://stackoverflow.com/questions/1165352/fast-comparison-between-two-python-dictionary/1165552#1165552
License: MIT
"""

import hashlib

class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.current_keys, self.past_keys = [
            set(d.keys()) for d in (current_dict, past_dict)
        ]
        self.intersect = self.current_keys.intersection(self.past_keys)

    @property
    def added(self):
        return self.current_keys - self.intersect

    @property
    def removed(self):
        return self.past_keys - self.intersect

    @property
    def changed(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])

    @property
    def unchanged(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])

    @property
    def identical(self):
        return self.current_dict == self.past_dict

def sha1_from_file(fname):
    sha1 = hashlib.sha1()
    with open(fname,'rb') as f:
        for chunk in iter(lambda: f.read(128*sha1.block_size), b''):
            sha1.update(chunk)
        return sha1.hexdigest()
