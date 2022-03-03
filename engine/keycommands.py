# ibus-byrninpikak - byrninpikak IME
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

from constants import *
from keyandstate import KeyAndState
from gi import require_version
require_version('IBus', '1.0')
from gi.repository import IBus

COMMANDS = {
    EISUU_MODE: {
        GO_INTO_KANA_MODE: {
            (IBus.Henkan, 0),
            (IBus.j, IBus.ModifierType.CONTROL_MASK)},
    },

    KANA_MODE: {
        GO_INTO_EISUU_MODE: {
            (IBus.Muhenkan, 0),
            (IBus.k, IBus.ModifierType.CONTROL_MASK)},
        DELETE: {
            (IBus.BackSpace, 0)},
        INPUT_SPACE: {
            (IBus.space, IBus.ModifierType.SHIFT_MASK)},
        GO_INTO_PRECONVERT_MODE: {
            (IBus.space, 0)},
    },

    PRECONVERT_MODE: {
        GO_INTO_EISUU_MODE: {
            (IBus.Muhenkan, 0),
            (IBus.k, IBus.ModifierType.CONTROL_MASK)},
        DELETE: {
            (IBus.BackSpace, 0)},
        INPUT_SPACE: {
            (IBus.space, IBus.ModifierType.SHIFT_MASK)},
        CONFIRM: {
            (IBus.Return, 0)},
        CANCEL: {
            (IBus.Escape, 0)},
        GO_INTO_CONVERT_MODE: {
            (IBus.space, 0)},
        TO_HIRAGANA: {
            (IBus.y, IBus.ModifierType.CONTROL_MASK)},
        TO_KATAKANA: {
            (IBus.u, IBus.ModifierType.CONTROL_MASK)},
        TO_HANKAKU_KATAKANA: {
            (IBus.i, IBus.ModifierType.CONTROL_MASK)},
        TO_EISUU: {
            (IBus.o, IBus.ModifierType.CONTROL_MASK)},
        TO_ZENKAKU_EISUU: {
            (IBus.p, IBus.ModifierType.CONTROL_MASK)},
    },

    CONVERT_MODE: {
        DELETE: {
            (IBus.BackSpace, 0)},
        PAGE_DOWN: {
            (IBus.space, 0)},
        PAGE_UP: {
            (IBus.space, IBus.ModifierType.SHIFT_MASK)},
        CONFIRM: {
            (IBus.Return, 0)},
        CANCEL: {
            (IBus.Escape, 0)},
        TO_HIRAGANA: {
            (IBus.y, IBus.ModifierType.CONTROL_MASK)},
        TO_KATAKANA: {
            (IBus.u, IBus.ModifierType.CONTROL_MASK)},
        TO_HANKAKU_KATAKANA: {
            (IBus.i, IBus.ModifierType.CONTROL_MASK)},
        TO_EISUU: {
            (IBus.o, IBus.ModifierType.CONTROL_MASK)},
        TO_ZENKAKU_EISUU: {
            (IBus.p, IBus.ModifierType.CONTROL_MASK)},
    },
}

def is_input_defined_as_command(ks, m, c):
    if (ks.keyval, ks.state) in COMMANDS[m][c]:
        return True
    return False
