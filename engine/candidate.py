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

class Candidate:
    def __init__(self, converted, key_pattern):
        self.converted = converted
        self.key_pattern = key_pattern

    @classmethod
    def is_there_converted_in_list(cls, o, l):
        for candidate in l:
            if o == candidate.converted:
                return True
        return False

    @classmethod
    def get_key_patterns_from_candidates(cls, l):
        r = []
        for candidate in l:
            r.append(candidate.key_pattern)
        return r
        
    def __eq__(self, c):
        if isinstance(c, Candidate):
            return self.converted == c.converted
        return False

    def __str__(self):
        return '%s, %s' % (self.converted, self.key_pattern)
