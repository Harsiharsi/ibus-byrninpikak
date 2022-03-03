# ibus-byrninpikak - byrninpikak IME
#
# Using source code derived from
#   ibus-tmpl - The Input Bus template project
# and
#   ibus-hiragana - ひらがなIME for IBus
#
# Copyright (c) 2022 Harsiharsi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import copy
import jaconv
from gi import require_version
require_version('IBus', '1.0')
from gi.repository import IBus

from constants import *
from candidate import Candidate
from keyandstate import KeyAndState
import keypatterns
from keycommands import *

keysyms = IBus

class EngineByrninpikak(IBus.Engine):
    __gtype_name__ = 'EngineByrninpikak'

    def __init__(self):
        super(EngineByrninpikak, self).__init__()

        self.__mode = EISUU_MODE

        self.__keyandstate = KeyAndState(None, None)

        self.__key_to_kana_table = self.set_input_to_kana_table()

        self.__preedit_yomi_string = ''
        self.__preedit_kana_string = ''
        self.__candidate_select_code = ''
        self.__raw_key_inputs = ''

        self.__lookup_table = IBus.LookupTable.new(10, 0, True, False)
        self.__lookup_table.set_orientation(IBus.Orientation.VERTICAL)
        self.__dictionary = self.set_dictionary()
        self.__candidate_list = []

        symbol = 'A'
        self.__prop_list = IBus.PropList()
        self.__input_mode_prop = IBus.Property(
            key = 'InputMode',
            prop_type = IBus.PropType.NORMAL,
            symbol = IBus.Text.new_from_string(symbol),
            label = IBus.Text.new_from_string('Input mode (%s)' % symbol),
            icon = None,
            tooltip = None,
            sensitive = False,
            visible = True,
            state = IBus.PropState.UNCHECKED,
            sub_props = None)
        self.__prop_list.append(self.__input_mode_prop)

    def __update_input_mode(self):
        if self.__mode == EISUU_MODE:
            symbol = 'A'
        else:
            symbol = 'あ'
        self.__input_mode_prop.set_symbol(IBus.Text.new_from_string(symbol))
        self.__input_mode_prop.set_label(IBus.Text.new_from_string('Input mode (%s)' % symbol))
        self.update_property(self.__input_mode_prop)

    def set_input_to_kana_table(self):
        #path = os.path.join(os.getenv('IBUS_BYRNINPIKAK_LOCATION'), 'key_to_kana_table.txt')
        path = 'key_to_kana_table.txt'
        t = {}
        with open(path, 'r', encoding='UTF-8-sig') as f:
            for l in f:
                p = l.strip(' \n').split('\t')
                if len(p) >= 3:
                    t[p[0]] = (p[1], p[2])
                elif len(p) == 2:
                    t[p[0]] = (p[1], '')
                else:
                    continue
        return t

    def set_dictionary(self):
        #path = os.path.join(os.getenv('IBUS_BYRNINPIKAK_LOCATION'), 'SKK-JISYO.ML')
        path = 'SKK-JISYO.ML'
        dictionary = {}
        is_okuriari = True
        okuri_key_tmp = 'a' #self.OKURI_KEY
        with open(path, 'r', encoding='euc-jp') as f:
            for l in f:
                if 'okuri-nasi' in l:
                    is_okuriari = False
                    okuri_key_tmp = ''
                    continue
                elif l[0] == ';':
                    continue

                p = re.sub(r';.+?/', '/', l).strip(' \n/').split(' ', 1)
                if is_okuriari:
                    yomi = p[0][0:-1]
                else:
                    yomi = p[0]
                parsed_candidates = p[1].strip(' \n/').split('/')

                candidates = []
                for i, pc in enumerate(parsed_candidates):
                    patterns = keypatterns.patterns.copy()
                    if dictionary.get(yomi) != None:
                        if Candidate.is_there_converted_in_list(pc, dictionary[yomi]):
                            continue

                        for p in keypatterns.patterns:
                            if okuri_key_tmp + p in Candidate.get_key_patterns_from_candidates(dictionary[yomi]):
                                patterns.remove(p)

                    candidates.append(Candidate(pc, okuri_key_tmp + patterns[i]))

                if dictionary.get(yomi) != None:
                    dictionary[yomi].extend(candidates)
                else:
                    dictionary[yomi] = candidates
        return dictionary

    def do_process_key_event(self, keyval, keycode, state):
        # ignore key release events
        is_press = ((state & IBus.ModifierType.RELEASE_MASK) == 0)
        if not is_press:
            return False

        self.__keyandstate.keyval = keyval
        self.__keyandstate.state = state & (
            IBus.ModifierType.SHIFT_MASK |
            IBus.ModifierType.CONTROL_MASK |
            IBus.ModifierType.MOD1_MASK)

        if self.__mode == EISUU_MODE:
            return self.eisuu_mode()
        elif self.__mode == KANA_MODE:
            return self.kana_mode()
        elif self.__mode == PRECONVERT_MODE:
            return self.preconvert_mode()
        elif self.__mode == CONVERT_MODE:
            return self.convert_mode()

        return False

    def eisuu_mode(self):
        if is_input_defined_as_command(
                self.__keyandstate, EISUU_MODE, GO_INTO_KANA_MODE):
            self.__mode = KANA_MODE
            self.__update_input_mode()
            self.__reset_field()
            return True

        return False

    def kana_mode(self):
        if is_input_defined_as_command(
                self.__keyandstate, KANA_MODE, GO_INTO_EISUU_MODE):
            self.__mode = EISUU_MODE
            self.__update_input_mode()
            self.__reset_field()
            return True

        elif (self.__keyandstate.state == 0 or \
                self.__keyandstate.state == IBus.ModifierType.SHIFT_MASK) and \
                self.__keyandstate.keyval >= keysyms.exclam and \
                self.__keyandstate.keyval <= keysyms.asciitilde:
            #self.__preedit_kana_string += chr(self.__keyandstate.keyval)
            r = self.handle_preedit_string(self.__preedit_kana_string,
                                            chr(self.__keyandstate.keyval))
            if r[0] != '':
                self.__commit_string(r[0])
            self.__preedit_kana_string = r[1]
            self.__update_preedit_text(self.__preedit_kana_string)
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, KANA_MODE, INPUT_SPACE):
            self.__commit_string(' ')
            self.__update_preedit_text(self.__preedit_kana_string)
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, KANA_MODE, DELETE):
            if self.__preedit_kana_string == '':
                return False
            self.__preedit_kana_string = self.__preedit_kana_string[:-1]
            self.__update_preedit_text(self.__preedit_kana_string)
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, KANA_MODE, GO_INTO_PRECONVERT_MODE):
            self.__commit_string(self.__preedit_kana_string)
            self.__mode = PRECONVERT_MODE
            self.__update_input_mode()
            self.__reset_field()
            self.__update_preedit_text(' ')
            return True

        else:
            self.__commit_string(self.__preedit_kana_string)
            self.__reset_field()
            return False

    def preconvert_mode(self):
        if is_input_defined_as_command(
                self.__keyandstate, PRECONVERT_MODE, GO_INTO_EISUU_MODE):
            self.__mode = EISUU_MODE
            self.__update_input_mode()
            self.__reset_field()
            return True

        elif (self.__keyandstate.state == 0 or \
                self.__keyandstate.state == IBus.ModifierType.SHIFT_MASK) and \
                self.__keyandstate.keyval >= keysyms.exclam and \
                self.__keyandstate.keyval <= keysyms.asciitilde:
            self.__raw_key_inputs += chr(self.__keyandstate.keyval) 
            #self.__preedit_kana_string += chr(self.__keyandstate.keyval)
            r = self.handle_preedit_string(self.__preedit_kana_string,
                                            chr(self.__keyandstate.keyval))
            self.__preedit_yomi_string += r[0]
            self.__preedit_kana_string = r[1]
            self.__update_preedit_text(
                self.__preedit_yomi_string + \
                self.__preedit_kana_string)
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, PRECONVERT_MODE, DELETE):
            self.__raw_key_inputs = self.__raw_key_inputs[0:-1]
            if self.__preedit_kana_string != '':
                self.__preedit_kana_string = self.__preedit_kana_string[0:-1]
                self.__update_preedit_text(
                    self.__preedit_yomi_string + \
                    self.__preedit_kana_string)
                return True
            self.__preedit_yomi_string = self.__preedit_yomi_string[0:-1]
            self.__update_preedit_text(
                self.__preedit_yomi_string + \
                self.__preedit_kana_string)
            if self.__preedit_yomi_string + self.__preedit_kana_string == '':
                self.__update_preedit_text(' ')
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, PRECONVERT_MODE, GO_INTO_CONVERT_MODE):
            if self.__preedit_yomi_string + self.__preedit_kana_string  in self.__dictionary:
                self.__candidate_list = self.__dictionary[self.__preedit_yomi_string + self.__preedit_kana_string]
            else:
                self.__candidate_list = []

            if len(self.__candidate_list) > 0:
                for c in self.__candidate_list:
                    self.__lookup_table.append_candidate(
                        IBus.Text.new_from_string(
                            c.converted + ' ' + c.key_pattern))

                self.__preedit_yomi_string += self.__preedit_kana_string
                self.__preedit_kana_string = ''
                self.__update_preedit_text(
                    self.__preedit_yomi_string + \
                    self.__preedit_kana_string)
                self.update_lookup_table(self.__lookup_table, True)
                self.__mode = CONVERT_MODE
                self.__update_input_mode()
                return True
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, PRECONVERT_MODE, TO_KATAKANA):
            self.__commit_string(jaconv.hira2kata(self.__preedit_yomi_string + self.__preedit_kana_string))
            self.__mode = KANA_MODE
            self.__update_input_mode()
            self.__reset_field()
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, PRECONVERT_MODE, TO_HANKAKU_KATAKANA):
            self.__commit_string(jaconv.hira2hkata(self.__preedit_yomi_string + self.__preedit_kana_string))
            self.__mode = KANA_MODE
            self.__update_input_mode()
            self.__reset_field()
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, PRECONVERT_MODE, TO_EISUU):
            self.__commit_string(self.__raw_key_inputs)
            self.__mode = KANA_MODE
            self.__update_input_mode()
            self.__reset_field()
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, PRECONVERT_MODE, TO_ZENKAKU_EISUU):
            self.__commit_string(jaconv.h2z(self.__raw_key_inputs, ascii=True, digit=True))
            self.__mode = KANA_MODE
            self.__update_input_mode()
            self.__reset_field()
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, PRECONVERT_MODE, CANCEL):
            self.__mode = KANA_MODE
            self.__update_input_mode()
            self.__reset_field()
            return True

        return False

    def convert_mode(self):
        if is_input_defined_as_command(
                self.__keyandstate, CONVERT_MODE, TO_EISUU):
            self.__mode = EISUU_MODE
            self.__update_input_mode()
            self.__reset_field()
            return True

        elif (self.__keyandstate.state == 0 or \
                self.__keyandstate.state == IBus.ModifierType.SHIFT_MASK) and \
                self.__keyandstate.keyval >= keysyms.exclam and \
                self.__keyandstate.keyval <= keysyms.asciitilde:

            self.__candidate_select_code += chr(self.__keyandstate.keyval)
            self.__update_preedit_text(
                self.__preedit_yomi_string + '' + \
                self.__candidate_select_code)
            self.when_candidate_select_code_changes()
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, CONVERT_MODE, DELETE):
                
            self.__candidate_select_code = self.__candidate_select_code[0:-1]
            self.__update_preedit_text(
                self.__preedit_yomi_string + '' + \
                self.__candidate_select_code)
            self.when_candidate_select_code_changes()
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, CONVERT_MODE, PAGE_DOWN):

            self.__lookup_table.page_down()
            self.update_lookup_table(self.__lookup_table, True)
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, CONVERT_MODE, PAGE_UP):

            self.__lookup_table.page_up()
            self.update_lookup_table(self.__lookup_table, True)
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, CONVERT_MODE, TO_KATAKANA):

            self.__commit_string(jaconv.hira2kata(self.__preedit_yomi_string + self.__preedit_kana_string))
            self.__mode = KANA_MODE
            self.__update_input_mode()
            self.__reset_field()
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, CONVERT_MODE, TO_HANKAKU_KATAKANA):

            self.__commit_string(jaconv.hira2hkata(self.__preedit_yomi_string + self.__preedit_kana_string))
            self.__mode = KANA_MODE
            self.__update_input_mode()
            self.__reset_field()
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, CONVERT_MODE, TO_EISUU):
                
            self.__commit_string(self.__raw_key_inputs)
            self.__mode = KANA_MODE
            self.__update_input_mode()
            self.__reset_field()
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, CONVERT_MODE, TO_ZENKAKU_EISUU):

            self.__commit_string(jaconv.h2z(self.__raw_key_inputs, ascii=True, digit=True))
            self.__mode = KANA_MODE
            self.__update_input_mode()
            self.__reset_field()
            return True

        elif is_input_defined_as_command(
                self.__keyandstate, CONVERT_MODE, CANCEL):

            self.__mode = PRECONVERT_MODE
            self.__update_input_mode()
            self.__candidate_select_code = ''
            self.__update_preedit_text(self.__preedit_yomi_string + self.__preedit_kana_string)
            self.__lookup_table.clear()
            self.hide_lookup_table()
            self.__candidate_list == []
            return True

        return False

    def when_candidate_select_code_changes(self):
        self.__lookup_table.clear()
        for c in self.__candidate_list:
            # 確定時
            if set(self.__candidate_select_code) == set(c.key_pattern):
                self.__commit_string(c.converted)
                self.__mode = KANA_MODE
                self.__reset_field()
                return
            # 候補選択コードが一致しないとき
            # 入力されたコードを含む候補を探す
            if set(self.__candidate_select_code) < set(c.key_pattern):
                self.__lookup_table.append_candidate(
                    IBus.Text.new_from_string(
                        c.converted + ' ' + c.key_pattern))
        self.update_lookup_table(self.__lookup_table, True)

    def handle_preedit_string(self, old, new):
        def is_there_definition_that_is_longer_than(s):
            for k in self.__key_to_kana_table.keys():
                if k.startswith(s) and k != s:
                    return True
            return False

        # 入力された文字列を先頭に含み、自身とは一致しない定義を探す
        # 最初に子音を入力するときなどに
        # その入力された文字列を未確定状態で出力する
        if is_there_definition_that_is_longer_than(old + new):
            return '', old + new

        elif old + new in self.__key_to_kana_table:
            return self.__key_to_kana_table[old + new]

        # 今の入力(new)よりまえに入力された文字列(old)を扱う
        # たとえば、普通のローマ字入力で「n」を押すと「n」としか出ない
        # 「n」と入力した途端に「ん」と表示されるとな行が打てないからである
        # つまり、それ自身が出力定義を持ちながら
        # それ自身に文字列をつけたした入力定義もほかにあるような
        # 入力定義についての処理を扱っている
        elif old in self.__key_to_kana_table:
            r = self.handle_preedit_string(new, '')
            return ''.join(self.__key_to_kana_table[old]) + r[0], r[1]

        # 入力された文字列が定義にない場合
        # すでに入力された文字列を先頭から1文字ずつ消して定義を探しなおす
        elif len(old) > 0:
            r = self.handle_preedit_string(old[1:], new)
            return old[0] + r[0], r[1]

        return old + new, ''

    def __update_preedit_text(self, s):
        u = IBus.AttrUnderline.SINGLE
        if self.__mode != KANA_MODE:
            u = IBus.AttrUnderline.DOUBLE

        al = IBus.AttrList()
        al.append(IBus.Attribute.new(
            IBus.AttrType.UNDERLINE, u, 0, len(s)))

        t = IBus.Text.new_from_string(s)
        t.set_attributes(al)

        self.update_preedit_text(t, len(s), len(s) > 0)

    def __commit_string(self, s):
        self.commit_text(IBus.Text.new_from_string(s))

    def __reset_field(self):
        self.__preedit_kana_string = ''
        self.__preedit_yomi_string = ''
        self.__raw_key_inputs = ''
        self.__candidate_select_code = ''
        self.__update_preedit_text('')
        self.__lookup_table.clear()
        self.hide_lookup_table()
        self.__candidate_list = []

    def do_focus_in(self):
        pass
        self.register_properties(self.__prop_list)

    def do_focus_out(self):
        if self.__mode != EISUU_MODE:
            self.__commit_string(self.__preedit_yomi_string + self.__preedit_kana_string)
            self.__mode = KANA_MODE
            self.__reset_field()

    def do_property_activate(self, prop_name):
        print("PropertyActivate(%s)" % prop_name)

if __name__ == '__main__':
    pass
