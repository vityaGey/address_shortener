#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import six

from . import abbrevs

########################################################################
# StreetAddressParser
########################################################################


class StreetAddressParser():
    def __init__(self):
        abbrev_suffix_map = get_abbrev_suffix_dict()
        self.street_type_set = set(abbrev_suffix_map.keys()) | set(abbrev_suffix_map.values())

        self.text2num_dict = get_text2num_dict()
        self.suite_type_set = set([
            'suite', 'ste',
            'apt', 'apartment', 'apartme', 'apartemen', 'apartado', 'apartament',
            'room', 'rm', '#',
            'unit', 'un', 'unt'
        ])
        self.rec_st_nd_rd_th = re.compile(r'^\d+(st|nd|rd|th)$', flags=re.I | re.U)
        self.rec_house_number = re.compile(r'^\d\S*$', flags=re.I | re.U)

    def parse(self, addr_str, skip_house=False):
        addr_str = addr_str.strip()
        res = {
            'house': None,
            'street_full': None,
            'other': None,
        }

        tokens = addr_str.split()
        start_idx = 0

        if len(tokens) == 0:
            return res

        if skip_house:
            start_idx = 0
        else:
            if tokens[0].lower() in self.text2num_dict:
                res['house'] = six.text_type(self.text2num_dict[tokens[0].lower()])
                start_idx = 1
            elif self.rec_st_nd_rd_th.search(tokens[0]):
                # first token is actually a street number (not house)
                start_idx = 0
            elif self.rec_house_number.search(tokens[0]):
                res['house'] = tokens[0]
                start_idx = 1
            else:
                # no house number
                start_idx = 0

            if res['house'] and len(tokens) >= 2 and tokens[1] == '1/2':
                res['house'] += ' ' + tokens[1]
                start_idx = 2

        street_accum = []
        other_accum = []
        is_in_state = 'street'  # can be 'street', 'suite', 'other'

        for i in range(start_idx, len(tokens)):
            word = tokens[i]
            #word = re.sub(r'[\.\,]+$', '', word, flags=re.I|re.U)
            while len(word) > 0 and (word[-1] == '.' or word[-1] == ','):
                # truncate the trailing dot (for abbrev)
                word = word[:-1]
            word_lw = word.lower()

            if word_lw in self.street_type_set and len(street_accum) > 0:
                res['street_type'] = word
                is_in_state = 'other'
            elif word_lw in self.suite_type_set:
                res['suite_type'] = word
                is_in_state = 'suite'
            elif len(word_lw) > 0 and word_lw[0] == '#' and res['suite_num'] is not None:
                res['suite_type'] = '#'
                res['suite_num'] = word[1:]
                is_in_state = 'other'
            elif is_in_state == 'street':
                street_accum.append(word)
            elif is_in_state == 'suite':
                res['suite_num'] = word
                is_in_state = 'other'
            elif is_in_state == 'other':
                other_accum.append(word)
            else:
                raise Exception('this state should never be reached')

        # TODO PO Box handling
        #acronym = lambda s : Regex(r"\.?\s*".join(s)+r"\.?")
        # poBoxRef = ((acronym("po") | acronym("apo") | acronym("afp")) +
        #            Optional(CaselessLiteral("BOX"))) + Word(alphanums)("boxnumber")

        if street_accum:
            res['street_name'] = ' ' . join(street_accum)
        if other_accum:
            res['other'] = ' ' . join(other_accum)

        if res['street_name'] and res['street_type']:
            res['street_full'] = res['street_name'] + ' ' + res['street_type']
        elif res['street_name']:
            res['street_full'] = res['street_name']
        elif res['street_type']:
            res['street_full'] = res['street_type']

        return res


def get_abbrev_suffix_dict():
    return abbrevs.USA_ABBREVS





########################################################################
# StreetAddressFormatter
########################################################################


        for k, v in self.abbrev_suffix_map.items():
            self.abbrev_suffix_map[k] = v.title()

        TH_or_str = '|' . join(self.street_type_set)
        self.re_TH = re.compile(r'\b(\d+)\s+(%s)\.?$' % TH_or_str, flags=re.I | re.U)



    def append_TH_to_street(self, addr):
        # street,avenue needs to be the last word
        addr = addr.strip()
        match = self.re_TH.search(addr)
        if match:
            repl = '%s %s' % (self.st_nd_th_convert(match.group(1)), match.group(2))
            addr = addr.replace(match.group(0), repl)
        return addr

    def abbrev_direction(self, addr):
        word_lst = addr.split()
        if len(word_lst) == 0:
            return addr

        for i in range(len(word_lst) - 1):
            word = word_lst[i].lower()
            # should have a digit after direction, e.g. "West 23rd"
            if word in self.abbrev_direction_map and word_lst[i + 1][0].isdigit():
                word_lst[i] = self.abbrev_direction_map[word]
        addr = ' ' . join(word_lst)
        return addr

    def abbrev_street_avenue_etc(self, addr, abbrev_only_last_token=True):
        word_lst = addr.split()
        if len(word_lst) == 0:
            return addr

        if abbrev_only_last_token:
            pos_lst = [-1]
        else:
            pos_lst = range(len(word_lst))

        for p in pos_lst:
            word = re.sub(r'\.$', '', word_lst[p]).lower()  # get rid of trailing period
            if word in self.abbrev_suffix_map:
                word_lst[p] = self.abbrev_suffix_map[word]
        addr = ' ' . join(word_lst)
        return addr
