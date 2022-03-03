# ibus-byrninpikak - byrninpikak IME
#
# Using source code derived from
#   ibus-tmpl - The Input Bus template project
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

engine_byrninpikak_PYTHON = \
    candidate.py \
	constants.py \
	engine.py \
	keyandstate.py \
    key_patterns.py \
    keycommands.py \
	main.py \
	$(NULL)

engine_byrninpikak_DATA = \
    key_to_kana_table.txt \
    SKK-JISYO.ML \
    $(NULL)

engine_byrninpikakdir = $(datadir)/ibus-byrninpikak

libexec_SCRIPTS = ibus-engine-byrninpikak

component_DATA = byrninpikak-python.xml
componentdir = @IBUS_DATADIR@/ibus/component

CLEANFILES = \
	$(NULL)

EXTRA_DIST = \
	ibus-engine-byrninpikak.in \
	byrninpikak-python.xml.in.in \
	$(NULL)

byrninpikak-python.xml: byrninpikak-python.xml.in
	$(AM_V_GEN) \
	( \
		libexecdir=${libexecdir}; \
		pkgdatadir=${pkgdatadir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@
