# ibus-byrninpikak - byrninpikak IME
#
# Using source code derived from
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

AC_INIT([ibus-byrninpikak], [0.0.0], [http://example.com])
AM_INIT_AUTOMAKE([foreign])

# Check IBus
#   Note byrninpikak-python.xml uses icon_prop_key and
#   ibus 1.5.11 or later is required
PKG_CHECK_MODULES(IBUS, [ibus-1.0 >= 1.5.11])
AC_SUBST(IBUS_DATADIR, $($PKG_CONFIG --variable=datadir ibus-1.0) )

# Check Python
AM_PATH_PYTHON([3.3])

# OUTPUT files
AC_CONFIG_FILES(Makefile
ibus-byrninpikak.spec
engine/Makefile
engine/ibus-engine-byrninpikak
engine/byrninpikak-python.xml.in
)

AC_OUTPUT
