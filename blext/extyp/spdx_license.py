# blext
# Copyright (C) 2025 blext Project Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Convenient list of SPDX licenses."""

import typing as typ

SPDXLicense: typ.TypeAlias = typ.Literal[
	'SPDX:0BSD',
	'SPDX:3D-Slicer-1.0',
	'SPDX:AAL',
	'SPDX:Abstyles',
	'SPDX:AdaCore-doc',
	'SPDX:Adobe-2006',
	'SPDX:Adobe-Display-PostScript',
	'SPDX:Adobe-Glyph',
	'SPDX:Adobe-Utopia',
	'SPDX:ADSL',
	'SPDX:AFL-1.1',
	'SPDX:AFL-1.2',
	'SPDX:AFL-2.0',
	'SPDX:AFL-2.1',
	'SPDX:AFL-3.0',
	'SPDX:Afmparse',
	'SPDX:AGPL-1.0',
	'SPDX:AGPL-1.0-only',
	'SPDX:AGPL-1.0-or-later',
	'SPDX:AGPL-3.0',
	'SPDX:AGPL-3.0-only',
	'SPDX:AGPL-3.0-or-later',
	'SPDX:Aladdin',
	'SPDX:AMD-newlib',
	'SPDX:AMDPLPA',
	'SPDX:AML',
	'SPDX:AML-glslang',
	'SPDX:AMPAS',
	'SPDX:ANTLR-PD',
	'SPDX:ANTLR-PD-fallback',
	'SPDX:any-OSI',
	'SPDX:Apache-1.0',
	'SPDX:Apache-1.1',
	'SPDX:Apache-2.0',
	'SPDX:APAFML',
	'SPDX:APL-1.0',
	'SPDX:App-s2p',
	'SPDX:APSL-1.0',
	'SPDX:APSL-1.1',
	'SPDX:APSL-1.2',
	'SPDX:APSL-2.0',
	'SPDX:Arphic-1999',
	'SPDX:Artistic-1.0',
	'SPDX:Artistic-1.0-cl8',
	'SPDX:Artistic-1.0-Perl',
	'SPDX:Artistic-2.0',
	'SPDX:ASWF-Digital-Assets-1.0',
	'SPDX:ASWF-Digital-Assets-1.1',
	'SPDX:Baekmuk',
	'SPDX:Bahyph',
	'SPDX:Barr',
	'SPDX:bcrypt-Solar-Designer',
	'SPDX:Beerware',
	'SPDX:Bitstream-Charter',
	'SPDX:Bitstream-Vera',
	'SPDX:BitTorrent-1.0',
	'SPDX:BitTorrent-1.1',
	'SPDX:blessing',
	'SPDX:BlueOak-1.0.0',
	'SPDX:Boehm-GC',
	'SPDX:Borceux',
	'SPDX:Brian-Gladman-2-Clause',
	'SPDX:Brian-Gladman-3-Clause',
	'SPDX:BSD-1-Clause',
	'SPDX:BSD-2-Clause',
	'SPDX:BSD-2-Clause-Darwin',
	'SPDX:BSD-2-Clause-first-lines',
	'SPDX:BSD-2-Clause-FreeBSD',
	'SPDX:BSD-2-Clause-NetBSD',
	'SPDX:BSD-2-Clause-Patent',
	'SPDX:BSD-2-Clause-Views',
	'SPDX:BSD-3-Clause',
	'SPDX:BSD-3-Clause-acpica',
	'SPDX:BSD-3-Clause-Attribution',
	'SPDX:BSD-3-Clause-Clear',
	'SPDX:BSD-3-Clause-flex',
	'SPDX:BSD-3-Clause-HP',
	'SPDX:BSD-3-Clause-LBNL',
	'SPDX:BSD-3-Clause-Modification',
	'SPDX:BSD-3-Clause-No-Military-License',
	'SPDX:BSD-3-Clause-No-Nuclear-License',
	'SPDX:BSD-3-Clause-No-Nuclear-License-2014',
	'SPDX:BSD-3-Clause-No-Nuclear-Warranty',
	'SPDX:BSD-3-Clause-Open-MPI',
	'SPDX:BSD-3-Clause-Sun',
	'SPDX:BSD-4-Clause',
	'SPDX:BSD-4-Clause-Shortened',
	'SPDX:BSD-4-Clause-UC',
	'SPDX:BSD-4.3RENO',
	'SPDX:BSD-4.3TAHOE',
	'SPDX:BSD-Advertising-Acknowledgement',
	'SPDX:BSD-Attribution-HPND-disclaimer',
	'SPDX:BSD-Inferno-Nettverk',
	'SPDX:BSD-Protection',
	'SPDX:BSD-Source-beginning-file',
	'SPDX:BSD-Source-Code',
	'SPDX:BSD-Systemics',
	'SPDX:BSD-Systemics-W3Works',
	'SPDX:BSL-1.0',
	'SPDX:BUSL-1.1',
	'SPDX:bzip2-1.0.5',
	'SPDX:bzip2-1.0.6',
	'SPDX:C-UDA-1.0',
	'SPDX:CAL-1.0',
	'SPDX:CAL-1.0-Combined-Work-Exception',
	'SPDX:Caldera',
	'SPDX:Caldera-no-preamble',
	'SPDX:Catharon',
	'SPDX:CATOSL-1.1',
	'SPDX:CC-BY-1.0',
	'SPDX:CC-BY-2.0',
	'SPDX:CC-BY-2.5',
	'SPDX:CC-BY-2.5-AU',
	'SPDX:CC-BY-3.0',
	'SPDX:CC-BY-3.0-AT',
	'SPDX:CC-BY-3.0-AU',
	'SPDX:CC-BY-3.0-DE',
	'SPDX:CC-BY-3.0-IGO',
	'SPDX:CC-BY-3.0-NL',
	'SPDX:CC-BY-3.0-US',
	'SPDX:CC-BY-4.0',
	'SPDX:CC-BY-NC-1.0',
	'SPDX:CC-BY-NC-2.0',
	'SPDX:CC-BY-NC-2.5',
	'SPDX:CC-BY-NC-3.0',
	'SPDX:CC-BY-NC-3.0-DE',
	'SPDX:CC-BY-NC-4.0',
	'SPDX:CC-BY-NC-ND-1.0',
	'SPDX:CC-BY-NC-ND-2.0',
	'SPDX:CC-BY-NC-ND-2.5',
	'SPDX:CC-BY-NC-ND-3.0',
	'SPDX:CC-BY-NC-ND-3.0-DE',
	'SPDX:CC-BY-NC-ND-3.0-IGO',
	'SPDX:CC-BY-NC-ND-4.0',
	'SPDX:CC-BY-NC-SA-1.0',
	'SPDX:CC-BY-NC-SA-2.0',
	'SPDX:CC-BY-NC-SA-2.0-DE',
	'SPDX:CC-BY-NC-SA-2.0-FR',
	'SPDX:CC-BY-NC-SA-2.0-UK',
	'SPDX:CC-BY-NC-SA-2.5',
	'SPDX:CC-BY-NC-SA-3.0',
	'SPDX:CC-BY-NC-SA-3.0-DE',
	'SPDX:CC-BY-NC-SA-3.0-IGO',
	'SPDX:CC-BY-NC-SA-4.0',
	'SPDX:CC-BY-ND-1.0',
	'SPDX:CC-BY-ND-2.0',
	'SPDX:CC-BY-ND-2.5',
	'SPDX:CC-BY-ND-3.0',
	'SPDX:CC-BY-ND-3.0-DE',
	'SPDX:CC-BY-ND-4.0',
	'SPDX:CC-BY-SA-1.0',
	'SPDX:CC-BY-SA-2.0',
	'SPDX:CC-BY-SA-2.0-UK',
	'SPDX:CC-BY-SA-2.1-JP',
	'SPDX:CC-BY-SA-2.5',
	'SPDX:CC-BY-SA-3.0',
	'SPDX:CC-BY-SA-3.0-AT',
	'SPDX:CC-BY-SA-3.0-DE',
	'SPDX:CC-BY-SA-3.0-IGO',
	'SPDX:CC-BY-SA-4.0',
	'SPDX:CC-PDDC',
	'SPDX:CC0-1.0',
	'SPDX:CDDL-1.0',
	'SPDX:CDDL-1.1',
	'SPDX:CDL-1.0',
	'SPDX:CDLA-Permissive-1.0',
	'SPDX:CDLA-Permissive-2.0',
	'SPDX:CDLA-Sharing-1.0',
	'SPDX:CECILL-1.0',
	'SPDX:CECILL-1.1',
	'SPDX:CECILL-2.0',
	'SPDX:CECILL-2.1',
	'SPDX:CECILL-B',
	'SPDX:CECILL-C',
	'SPDX:CERN-OHL-1.1',
	'SPDX:CERN-OHL-1.2',
	'SPDX:CERN-OHL-P-2.0',
	'SPDX:CERN-OHL-S-2.0',
	'SPDX:CERN-OHL-W-2.0',
	'SPDX:CFITSIO',
	'SPDX:check-cvs',
	'SPDX:checkmk',
	'SPDX:ClArtistic',
	'SPDX:Clips',
	'SPDX:CMU-Mach',
	'SPDX:CMU-Mach-nodoc',
	'SPDX:CNRI-Jython',
	'SPDX:CNRI-Python',
	'SPDX:CNRI-Python-GPL-Compatible',
	'SPDX:COIL-1.0',
	'SPDX:Community-Spec-1.0',
	'SPDX:Condor-1.1',
	'SPDX:copyleft-next-0.3.0',
	'SPDX:copyleft-next-0.3.1',
	'SPDX:Cornell-Lossless-JPEG',
	'SPDX:CPAL-1.0',
	'SPDX:CPL-1.0',
	'SPDX:CPOL-1.02',
	'SPDX:Cronyx',
	'SPDX:Crossword',
	'SPDX:CrystalStacker',
	'SPDX:CUA-OPL-1.0',
	'SPDX:Cube',
	'SPDX:curl',
	'SPDX:cve-tou',
	'SPDX:D-FSL-1.0',
	'SPDX:DEC-3-Clause',
	'SPDX:diffmark',
	'SPDX:DL-DE-BY-2.0',
	'SPDX:DL-DE-ZERO-2.0',
	'SPDX:DOC',
	'SPDX:Dotseqn',
	'SPDX:DRL-1.0',
	'SPDX:DRL-1.1',
	'SPDX:DSDP',
	'SPDX:dtoa',
	'SPDX:dvipdfm',
	'SPDX:ECL-1.0',
	'SPDX:ECL-2.0',
	'SPDX:eCos-2.0',
	'SPDX:EFL-1.0',
	'SPDX:EFL-2.0',
	'SPDX:eGenix',
	'SPDX:Elastic-2.0',
	'SPDX:Entessa',
	'SPDX:EPICS',
	'SPDX:EPL-1.0',
	'SPDX:EPL-2.0',
	'SPDX:ErlPL-1.1',
	'SPDX:etalab-2.0',
	'SPDX:EUDatagrid',
	'SPDX:EUPL-1.0',
	'SPDX:EUPL-1.1',
	'SPDX:EUPL-1.2',
	'SPDX:Eurosym',
	'SPDX:Fair',
	'SPDX:FBM',
	'SPDX:FDK-AAC',
	'SPDX:Ferguson-Twofish',
	'SPDX:Frameworx-1.0',
	'SPDX:FreeBSD-DOC',
	'SPDX:FreeImage',
	'SPDX:FSFAP',
	'SPDX:FSFAP-no-warranty-disclaimer',
	'SPDX:FSFUL',
	'SPDX:FSFULLR',
	'SPDX:FSFULLRWD',
	'SPDX:FTL',
	'SPDX:Furuseth',
	'SPDX:fwlw',
	'SPDX:GCR-docs',
	'SPDX:GD',
	'SPDX:GFDL-1.1',
	'SPDX:GFDL-1.1-invariants-only',
	'SPDX:GFDL-1.1-invariants-or-later',
	'SPDX:GFDL-1.1-no-invariants-only',
	'SPDX:GFDL-1.1-no-invariants-or-later',
	'SPDX:GFDL-1.1-only',
	'SPDX:GFDL-1.1-or-later',
	'SPDX:GFDL-1.2',
	'SPDX:GFDL-1.2-invariants-only',
	'SPDX:GFDL-1.2-invariants-or-later',
	'SPDX:GFDL-1.2-no-invariants-only',
	'SPDX:GFDL-1.2-no-invariants-or-later',
	'SPDX:GFDL-1.2-only',
	'SPDX:GFDL-1.2-or-later',
	'SPDX:GFDL-1.3',
	'SPDX:GFDL-1.3-invariants-only',
	'SPDX:GFDL-1.3-invariants-or-later',
	'SPDX:GFDL-1.3-no-invariants-only',
	'SPDX:GFDL-1.3-no-invariants-or-later',
	'SPDX:GFDL-1.3-only',
	'SPDX:GFDL-1.3-or-later',
	'SPDX:Giftware',
	'SPDX:GL2PS',
	'SPDX:Glide',
	'SPDX:Glulxe',
	'SPDX:GLWTPL',
	'SPDX:gnuplot',
	'SPDX:GPL-1.0',
	'SPDX:GPL-1.0+',
	'SPDX:GPL-1.0-only',
	'SPDX:GPL-1.0-or-later',
	'SPDX:GPL-2.0',
	'SPDX:GPL-2.0+',
	'SPDX:GPL-2.0-only',
	'SPDX:GPL-2.0-or-later',
	'SPDX:GPL-2.0-with-autoconf-exception',
	'SPDX:GPL-2.0-with-bison-exception',
	'SPDX:GPL-2.0-with-classpath-exception',
	'SPDX:GPL-2.0-with-font-exception',
	'SPDX:GPL-2.0-with-GCC-exception',
	'SPDX:GPL-3.0',
	'SPDX:GPL-3.0+',
	'SPDX:GPL-3.0-only',
	'SPDX:GPL-3.0-or-later',
	'SPDX:GPL-3.0-with-autoconf-exception',
	'SPDX:GPL-3.0-with-GCC-exception',
	'SPDX:Graphics-Gems',
	'SPDX:gSOAP-1.3b',
	'SPDX:gtkbook',
	'SPDX:Gutmann',
	'SPDX:HaskellReport',
	'SPDX:hdparm',
	'SPDX:Hippocratic-2.1',
	'SPDX:HP-1986',
	'SPDX:HP-1989',
	'SPDX:HPND',
	'SPDX:HPND-DEC',
	'SPDX:HPND-doc',
	'SPDX:HPND-doc-sell',
	'SPDX:HPND-export-US',
	'SPDX:HPND-export-US-acknowledgement',
	'SPDX:HPND-export-US-modify',
	'SPDX:HPND-export2-US',
	'SPDX:HPND-Fenneberg-Livingston',
	'SPDX:HPND-INRIA-IMAG',
	'SPDX:HPND-Intel',
	'SPDX:HPND-Kevlin-Henney',
	'SPDX:HPND-Markus-Kuhn',
	'SPDX:HPND-merchantability-variant',
	'SPDX:HPND-MIT-disclaimer',
	'SPDX:HPND-Pbmplus',
	'SPDX:HPND-sell-MIT-disclaimer-xserver',
	'SPDX:HPND-sell-regexpr',
	'SPDX:HPND-sell-variant',
	'SPDX:HPND-sell-variant-MIT-disclaimer',
	'SPDX:HPND-sell-variant-MIT-disclaimer-rev',
	'SPDX:HPND-UC',
	'SPDX:HPND-UC-export-US',
	'SPDX:HTMLTIDY',
	'SPDX:IBM-pibs',
	'SPDX:ICU',
	'SPDX:IEC-Code-Components-EULA',
	'SPDX:IJG',
	'SPDX:IJG-short',
	'SPDX:ImageMagick',
	'SPDX:iMatix',
	'SPDX:Imlib2',
	'SPDX:Info-ZIP',
	'SPDX:Inner-Net-2.0',
	'SPDX:Intel',
	'SPDX:Intel-ACPI',
	'SPDX:Interbase-1.0',
	'SPDX:IPA',
	'SPDX:IPL-1.0',
	'SPDX:ISC',
	'SPDX:ISC-Veillard',
	'SPDX:Jam',
	'SPDX:JasPer-2.0',
	'SPDX:JPL-image',
	'SPDX:JPNIC',
	'SPDX:JSON',
	'SPDX:Kastrup',
	'SPDX:Kazlib',
	'SPDX:Knuth-CTAN',
	'SPDX:LAL-1.2',
	'SPDX:LAL-1.3',
	'SPDX:Latex2e',
	'SPDX:Latex2e-translated-notice',
	'SPDX:Leptonica',
	'SPDX:LGPL-2.0',
	'SPDX:LGPL-2.0+',
	'SPDX:LGPL-2.0-only',
	'SPDX:LGPL-2.0-or-later',
	'SPDX:LGPL-2.1',
	'SPDX:LGPL-2.1+',
	'SPDX:LGPL-2.1-only',
	'SPDX:LGPL-2.1-or-later',
	'SPDX:LGPL-3.0',
	'SPDX:LGPL-3.0+',
	'SPDX:LGPL-3.0-only',
	'SPDX:LGPL-3.0-or-later',
	'SPDX:LGPLLR',
	'SPDX:Libpng',
	'SPDX:libpng-2.0',
	'SPDX:libselinux-1.0',
	'SPDX:libtiff',
	'SPDX:libutil-David-Nugent',
	'SPDX:LiLiQ-P-1.1',
	'SPDX:LiLiQ-R-1.1',
	'SPDX:LiLiQ-Rplus-1.1',
	'SPDX:Linux-man-pages-1-para',
	'SPDX:Linux-man-pages-copyleft',
	'SPDX:Linux-man-pages-copyleft-2-para',
	'SPDX:Linux-man-pages-copyleft-var',
	'SPDX:Linux-OpenIB',
	'SPDX:LOOP',
	'SPDX:LPD-document',
	'SPDX:LPL-1.0',
	'SPDX:LPL-1.02',
	'SPDX:LPPL-1.0',
	'SPDX:LPPL-1.1',
	'SPDX:LPPL-1.2',
	'SPDX:LPPL-1.3a',
	'SPDX:LPPL-1.3c',
	'SPDX:lsof',
	'SPDX:Lucida-Bitmap-Fonts',
	'SPDX:LZMA-SDK-9.11-to-9.20',
	'SPDX:LZMA-SDK-9.22',
	'SPDX:Mackerras-3-Clause',
	'SPDX:Mackerras-3-Clause-acknowledgment',
	'SPDX:magaz',
	'SPDX:mailprio',
	'SPDX:MakeIndex',
	'SPDX:Martin-Birgmeier',
	'SPDX:McPhee-slideshow',
	'SPDX:metamail',
	'SPDX:Minpack',
	'SPDX:MirOS',
	'SPDX:MIT',
	'SPDX:MIT-0',
	'SPDX:MIT-advertising',
	'SPDX:MIT-CMU',
	'SPDX:MIT-enna',
	'SPDX:MIT-feh',
	'SPDX:MIT-Festival',
	'SPDX:MIT-Khronos-old',
	'SPDX:MIT-Modern-Variant',
	'SPDX:MIT-open-group',
	'SPDX:MIT-testregex',
	'SPDX:MIT-Wu',
	'SPDX:MITNFA',
	'SPDX:MMIXware',
	'SPDX:Motosoto',
	'SPDX:MPEG-SSG',
	'SPDX:mpi-permissive',
	'SPDX:mpich2',
	'SPDX:MPL-1.0',
	'SPDX:MPL-1.1',
	'SPDX:MPL-2.0',
	'SPDX:MPL-2.0-no-copyleft-exception',
	'SPDX:mplus',
	'SPDX:MS-LPL',
	'SPDX:MS-PL',
	'SPDX:MS-RL',
	'SPDX:MTLL',
	'SPDX:MulanPSL-1.0',
	'SPDX:MulanPSL-2.0',
	'SPDX:Multics',
	'SPDX:Mup',
	'SPDX:NAIST-2003',
	'SPDX:NASA-1.3',
	'SPDX:Naumen',
	'SPDX:NBPL-1.0',
	'SPDX:NCBI-PD',
	'SPDX:NCGL-UK-2.0',
	'SPDX:NCL',
	'SPDX:NCSA',
	'SPDX:Net-SNMP',
	'SPDX:NetCDF',
	'SPDX:Newsletr',
	'SPDX:NGPL',
	'SPDX:NICTA-1.0',
	'SPDX:NIST-PD',
	'SPDX:NIST-PD-fallback',
	'SPDX:NIST-Software',
	'SPDX:NLOD-1.0',
	'SPDX:NLOD-2.0',
	'SPDX:NLPL',
	'SPDX:Nokia',
	'SPDX:NOSL',
	'SPDX:Noweb',
	'SPDX:NPL-1.0',
	'SPDX:NPL-1.1',
	'SPDX:NPOSL-3.0',
	'SPDX:NRL',
	'SPDX:NTP',
	'SPDX:NTP-0',
	'SPDX:Nunit',
	'SPDX:O-UDA-1.0',
	'SPDX:OAR',
	'SPDX:OCCT-PL',
	'SPDX:OCLC-2.0',
	'SPDX:ODbL-1.0',
	'SPDX:ODC-By-1.0',
	'SPDX:OFFIS',
	'SPDX:OFL-1.0',
	'SPDX:OFL-1.0-no-RFN',
	'SPDX:OFL-1.0-RFN',
	'SPDX:OFL-1.1',
	'SPDX:OFL-1.1-no-RFN',
	'SPDX:OFL-1.1-RFN',
	'SPDX:OGC-1.0',
	'SPDX:OGDL-Taiwan-1.0',
	'SPDX:OGL-Canada-2.0',
	'SPDX:OGL-UK-1.0',
	'SPDX:OGL-UK-2.0',
	'SPDX:OGL-UK-3.0',
	'SPDX:OGTSL',
	'SPDX:OLDAP-1.1',
	'SPDX:OLDAP-1.2',
	'SPDX:OLDAP-1.3',
	'SPDX:OLDAP-1.4',
	'SPDX:OLDAP-2.0',
	'SPDX:OLDAP-2.0.1',
	'SPDX:OLDAP-2.1',
	'SPDX:OLDAP-2.2',
	'SPDX:OLDAP-2.2.1',
	'SPDX:OLDAP-2.2.2',
	'SPDX:OLDAP-2.3',
	'SPDX:OLDAP-2.4',
	'SPDX:OLDAP-2.5',
	'SPDX:OLDAP-2.6',
	'SPDX:OLDAP-2.7',
	'SPDX:OLDAP-2.8',
	'SPDX:OLFL-1.3',
	'SPDX:OML',
	'SPDX:OpenPBS-2.3',
	'SPDX:OpenSSL',
	'SPDX:OpenSSL-standalone',
	'SPDX:OpenVision',
	'SPDX:OPL-1.0',
	'SPDX:OPL-UK-3.0',
	'SPDX:OPUBL-1.0',
	'SPDX:OSET-PL-2.1',
	'SPDX:OSL-1.0',
	'SPDX:OSL-1.1',
	'SPDX:OSL-2.0',
	'SPDX:OSL-2.1',
	'SPDX:OSL-3.0',
	'SPDX:PADL',
	'SPDX:Parity-6.0.0',
	'SPDX:Parity-7.0.0',
	'SPDX:PDDL-1.0',
	'SPDX:PHP-3.0',
	'SPDX:PHP-3.01',
	'SPDX:Pixar',
	'SPDX:pkgconf',
	'SPDX:Plexus',
	'SPDX:pnmstitch',
	'SPDX:PolyForm-Noncommercial-1.0.0',
	'SPDX:PolyForm-Small-Business-1.0.0',
	'SPDX:PostgreSQL',
	'SPDX:PPL',
	'SPDX:PSF-2.0',
	'SPDX:psfrag',
	'SPDX:psutils',
	'SPDX:Python-2.0',
	'SPDX:Python-2.0.1',
	'SPDX:python-ldap',
	'SPDX:Qhull',
	'SPDX:QPL-1.0',
	'SPDX:QPL-1.0-INRIA-2004',
	'SPDX:radvd',
	'SPDX:Rdisc',
	'SPDX:RHeCos-1.1',
	'SPDX:RPL-1.1',
	'SPDX:RPL-1.5',
	'SPDX:RPSL-1.0',
	'SPDX:RSA-MD',
	'SPDX:RSCPL',
	'SPDX:Ruby',
	'SPDX:SAX-PD',
	'SPDX:SAX-PD-2.0',
	'SPDX:Saxpath',
	'SPDX:SCEA',
	'SPDX:SchemeReport',
	'SPDX:Sendmail',
	'SPDX:Sendmail-8.23',
	'SPDX:SGI-B-1.0',
	'SPDX:SGI-B-1.1',
	'SPDX:SGI-B-2.0',
	'SPDX:SGI-OpenGL',
	'SPDX:SGP4',
	'SPDX:SHL-0.5',
	'SPDX:SHL-0.51',
	'SPDX:SimPL-2.0',
	'SPDX:SISSL',
	'SPDX:SISSL-1.2',
	'SPDX:SL',
	'SPDX:Sleepycat',
	'SPDX:SMLNJ',
	'SPDX:SMPPL',
	'SPDX:SNIA',
	'SPDX:snprintf',
	'SPDX:softSurfer',
	'SPDX:Soundex',
	'SPDX:Spencer-86',
	'SPDX:Spencer-94',
	'SPDX:Spencer-99',
	'SPDX:SPL-1.0',
	'SPDX:ssh-keyscan',
	'SPDX:SSH-OpenSSH',
	'SPDX:SSH-short',
	'SPDX:SSLeay-standalone',
	'SPDX:SSPL-1.0',
	'SPDX:StandardML-NJ',
	'SPDX:SugarCRM-1.1.3',
	'SPDX:Sun-PPP',
	'SPDX:Sun-PPP-2000',
	'SPDX:SunPro',
	'SPDX:SWL',
	'SPDX:swrule',
	'SPDX:Symlinks',
	'SPDX:TAPR-OHL-1.0',
	'SPDX:TCL',
	'SPDX:TCP-wrappers',
	'SPDX:TermReadKey',
	'SPDX:TGPPL-1.0',
	'SPDX:threeparttable',
	'SPDX:TMate',
	'SPDX:TORQUE-1.1',
	'SPDX:TOSL',
	'SPDX:TPDL',
	'SPDX:TPL-1.0',
	'SPDX:TTWL',
	'SPDX:TTYP0',
	'SPDX:TU-Berlin-1.0',
	'SPDX:TU-Berlin-2.0',
	'SPDX:UCAR',
	'SPDX:UCL-1.0',
	'SPDX:ulem',
	'SPDX:UMich-Merit',
	'SPDX:Unicode-3.0',
	'SPDX:Unicode-DFS-2015',
	'SPDX:Unicode-DFS-2016',
	'SPDX:Unicode-TOU',
	'SPDX:UnixCrypt',
	'SPDX:Unlicense',
	'SPDX:UPL-1.0',
	'SPDX:URT-RLE',
	'SPDX:Vim',
	'SPDX:VOSTROM',
	'SPDX:VSL-1.0',
	'SPDX:W3C',
	'SPDX:W3C-19980720',
	'SPDX:W3C-20150513',
	'SPDX:w3m',
	'SPDX:Watcom-1.0',
	'SPDX:Widget-Workshop',
	'SPDX:Wsuipa',
	'SPDX:WTFPL',
	'SPDX:wxWindows',
	'SPDX:X11',
	'SPDX:X11-distribute-modifications-variant',
	'SPDX:Xdebug-1.03',
	'SPDX:Xerox',
	'SPDX:Xfig',
	'SPDX:XFree86-1.1',
	'SPDX:xinetd',
	'SPDX:xkeyboard-config-Zinoviev',
	'SPDX:xlock',
	'SPDX:Xnet',
	'SPDX:xpp',
	'SPDX:XSkat',
	'SPDX:xzoom',
	'SPDX:YPL-1.0',
	'SPDX:YPL-1.1',
	'SPDX:Zed',
	'SPDX:Zeeff',
	'SPDX:Zend-2.0',
	'SPDX:Zimbra-1.3',
	'SPDX:Zimbra-1.4',
	'SPDX:Zlib',
	'SPDX:zlib-acknowledgement',
	'SPDX:ZPL-1.1',
	'SPDX:ZPL-2.0',
	'SPDX:ZPL-2.1',
]
