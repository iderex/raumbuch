"""The catalogue corpus: one refused set of records per reason, and a near miss.

The corpus in `corpus.py` is one document per fixture, because the loader reads
one document. The reasons in this file need more than one, or need a pin beside
the records, so a fixture here is a set of records and optionally the pair a
consumer held. Everything else is the same discipline: the refused half triggers
exactly its own reason, the accepted half beside it is one plausible mistake
away and is accepted, and the note says what the one difference is.

Every record is base64, for the reason `corpus.py` gives at length: a raw TOML
literal in a tracked text file is normalised on the way into git and on the way
out, and normalisation deletes bytes a fixture may exist to prove. The records
here are the smallest thing the loader accepts rather than the worked
Schwarzschild record, because what these fixtures are about is the set and not
the contents of any member of it.

To add one: write the records to files, encode each with

    python3 -m base64 fixture.toml

and paste the lines in beside its reason.
"""

from __future__ import annotations

import base64
import dataclasses


@dataclasses.dataclass(frozen=True)
class Half:
    """A catalogue, and what a consumer had pinned when it read one.

    ``documents`` are ``(source, base64)`` pairs, where the source is the name
    the record would have been read out of. ``pin`` is the ``(id, version)`` a
    consumer held, or ``None`` where the fixture is about the records alone.
    """

    documents: tuple[tuple[str, str], ...]
    pin: tuple[str, int] | None = None

    def decoded(self) -> list[tuple[str, bytes]]:
        return [(source, base64.b64decode(data)) for source, data in self.documents]


@dataclasses.dataclass(frozen=True)
class Fixture:
    """One refused catalogue, the near miss beside it, and what separates them."""

    refused: Half
    accepted: Half
    note: str


#: The smallest record the loader accepts, at version 1, spending the id
#: ``kerr`` and claiming no relation to any other record.
KERR = (
    "CnNjaGVtYV92ZXJzaW9uID0gIjEiCgppZCA9ICJrZXJyIgp2ZXJzaW9uID0gMQpuYW1l"
    "ID0gIktlcnIiCmRpbWVuc2lvbiA9IDQKc2lnbmF0dXJlID0gIi0rKysiCgpjb3ZlcmFn"
    "ZV9hcmd1bWVudCA9ICJPbmUgc3RyYXR1bSwgbWFya2VkIGdlbmVyaWMsIHdob3NlIGNv"
    "bmRpdGlvbiBpcyB0aGUgZGVjbGFyZWQgcmFuZ2UgTSA+IDAgb2YgdGhlIG9uZSBwYXJh"
    "bWV0ZXIuIE5vdGhpbmcgbGllcyBvdXRzaWRlIGl0LCBzbyB0aGUgc3RyYXRhIGNvdmVy"
    "IHRoZSByYW5nZS4iCgpbW3BhcmFtZXRlcl1dCm5hbWUgPSAiTSIKZG9tYWluID0gInJl"
    "YWwiCnJhbmdlID0gIk0gPiAwIgptZWFuaW5nID0gIm1hc3MgcGFyYW1ldGVyIgoKW21h"
    "dHRlcl0KbW9kZWwgPSAidmFjdXVtIgoKW1tzdHJhdHVtXV0KbmFtZSA9ICJnZW5lcmlj"
    "IgpnZW5lcmljID0gdHJ1ZQpjb25kaXRpb24gPSAiTSA+IDAiCgpbW2NoYXJ0XV0KbmFt"
    "ZSA9ICJleHRlcmlvciIKY29vcmRpbmF0ZXMgPSBbInQiLCAiciIsICJ0aGV0YSIsICJw"
    "aGkiXQpyZWdpb24gPSAidGhlIHN0YXRpYyByZWdpb24gb3V0c2lkZSB0aGUgaG9yaXpv"
    "biIKcmFuZ2UgPSBbInIgPiAyKk0iXQoKW1tjaGFydC5tZXRyaWNdXQppID0gInQiCmog"
    "PSAidCIKdmFsdWUgPSAiLSgxIC0gMipNL3IpIgoKW1tjaGFydC5tZXRyaWNdXQppID0g"
    "InIiCmogPSAiciIKdmFsdWUgPSAiMS8oMSAtIDIqTS9yKSIKCltbY2hhcnQubWV0cmlj"
    "XV0KaSA9ICJ0aGV0YSIKaiA9ICJ0aGV0YSIKdmFsdWUgPSAicl4yIgoKW1tjaGFydC5t"
    "ZXRyaWNdXQppID0gInBoaSIKaiA9ICJwaGkiCnZhbHVlID0gInJeMipzaW4odGhldGEp"
    "XjIiCgpbcHJvdmVuYW5jZV0Kc291cmNlX2tpbmQgPSAic2Vjb25kYXJ5IgpjaXRhdGlv"
    "biA9ICJ0byBiZSBmaWxsZWQgYnkgaXNzdWUgIzczIgpsb2NhdG9yID0gInRvIGJlIGZp"
    "bGxlZCBieSBpc3N1ZSAjNzMiCnRyYW5zY3JpYmVkX29uID0gIjIwMjYtMDgtMDciCg=="
)

#: The same record saying it has been superseded by ``kerr-schild``. On its
#: own that names a record nothing holds; beside the one below it is a link
#: written from both ends.
KERR_SUPERSEDED = (
    "CnNjaGVtYV92ZXJzaW9uID0gIjEiCgppZCA9ICJrZXJyIgp2ZXJzaW9uID0gMQpzdXBl"
    "cnNlZGVkX2J5ID0gImtlcnItc2NoaWxkIgpuYW1lID0gIktlcnIiCmRpbWVuc2lvbiA9"
    "IDQKc2lnbmF0dXJlID0gIi0rKysiCgpjb3ZlcmFnZV9hcmd1bWVudCA9ICJPbmUgc3Ry"
    "YXR1bSwgbWFya2VkIGdlbmVyaWMsIHdob3NlIGNvbmRpdGlvbiBpcyB0aGUgZGVjbGFy"
    "ZWQgcmFuZ2UgTSA+IDAgb2YgdGhlIG9uZSBwYXJhbWV0ZXIuIE5vdGhpbmcgbGllcyBv"
    "dXRzaWRlIGl0LCBzbyB0aGUgc3RyYXRhIGNvdmVyIHRoZSByYW5nZS4iCgpbW3BhcmFt"
    "ZXRlcl1dCm5hbWUgPSAiTSIKZG9tYWluID0gInJlYWwiCnJhbmdlID0gIk0gPiAwIgpt"
    "ZWFuaW5nID0gIm1hc3MgcGFyYW1ldGVyIgoKW21hdHRlcl0KbW9kZWwgPSAidmFjdXVt"
    "IgoKW1tzdHJhdHVtXV0KbmFtZSA9ICJnZW5lcmljIgpnZW5lcmljID0gdHJ1ZQpjb25k"
    "aXRpb24gPSAiTSA+IDAiCgpbW2NoYXJ0XV0KbmFtZSA9ICJleHRlcmlvciIKY29vcmRp"
    "bmF0ZXMgPSBbInQiLCAiciIsICJ0aGV0YSIsICJwaGkiXQpyZWdpb24gPSAidGhlIHN0"
    "YXRpYyByZWdpb24gb3V0c2lkZSB0aGUgaG9yaXpvbiIKcmFuZ2UgPSBbInIgPiAyKk0i"
    "XQoKW1tjaGFydC5tZXRyaWNdXQppID0gInQiCmogPSAidCIKdmFsdWUgPSAiLSgxIC0g"
    "MipNL3IpIgoKW1tjaGFydC5tZXRyaWNdXQppID0gInIiCmogPSAiciIKdmFsdWUgPSAi"
    "MS8oMSAtIDIqTS9yKSIKCltbY2hhcnQubWV0cmljXV0KaSA9ICJ0aGV0YSIKaiA9ICJ0"
    "aGV0YSIKdmFsdWUgPSAicl4yIgoKW1tjaGFydC5tZXRyaWNdXQppID0gInBoaSIKaiA9"
    "ICJwaGkiCnZhbHVlID0gInJeMipzaW4odGhldGEpXjIiCgpbcHJvdmVuYW5jZV0Kc291"
    "cmNlX2tpbmQgPSAic2Vjb25kYXJ5IgpjaXRhdGlvbiA9ICJ0byBiZSBmaWxsZWQgYnkg"
    "aXNzdWUgIzczIgpsb2NhdG9yID0gInRvIGJlIGZpbGxlZCBieSBpc3N1ZSAjNzMiCnRy"
    "YW5zY3JpYmVkX29uID0gIjIwMjYtMDgtMDciCg=="
)

#: A second record, spending a second id, claiming to displace nothing.
KERR_SCHILD = (
    "CnNjaGVtYV92ZXJzaW9uID0gIjEiCgppZCA9ICJrZXJyLXNjaGlsZCIKdmVyc2lvbiA9"
    "IDEKbmFtZSA9ICJLZXJyIGluIEtlcnItU2NoaWxkIGZvcm0iCmRpbWVuc2lvbiA9IDQK"
    "c2lnbmF0dXJlID0gIi0rKysiCgpjb3ZlcmFnZV9hcmd1bWVudCA9ICJPbmUgc3RyYXR1"
    "bSwgbWFya2VkIGdlbmVyaWMsIHdob3NlIGNvbmRpdGlvbiBpcyB0aGUgZGVjbGFyZWQg"
    "cmFuZ2UgTSA+IDAgb2YgdGhlIG9uZSBwYXJhbWV0ZXIuIE5vdGhpbmcgbGllcyBvdXRz"
    "aWRlIGl0LCBzbyB0aGUgc3RyYXRhIGNvdmVyIHRoZSByYW5nZS4iCgpbW3BhcmFtZXRl"
    "cl1dCm5hbWUgPSAiTSIKZG9tYWluID0gInJlYWwiCnJhbmdlID0gIk0gPiAwIgptZWFu"
    "aW5nID0gIm1hc3MgcGFyYW1ldGVyIgoKW21hdHRlcl0KbW9kZWwgPSAidmFjdXVtIgoK"
    "W1tzdHJhdHVtXV0KbmFtZSA9ICJnZW5lcmljIgpnZW5lcmljID0gdHJ1ZQpjb25kaXRp"
    "b24gPSAiTSA+IDAiCgpbW2NoYXJ0XV0KbmFtZSA9ICJleHRlcmlvciIKY29vcmRpbmF0"
    "ZXMgPSBbInQiLCAiciIsICJ0aGV0YSIsICJwaGkiXQpyZWdpb24gPSAidGhlIHN0YXRp"
    "YyByZWdpb24gb3V0c2lkZSB0aGUgaG9yaXpvbiIKcmFuZ2UgPSBbInIgPiAyKk0iXQoK"
    "W1tjaGFydC5tZXRyaWNdXQppID0gInQiCmogPSAidCIKdmFsdWUgPSAiLSgxIC0gMipN"
    "L3IpIgoKW1tjaGFydC5tZXRyaWNdXQppID0gInIiCmogPSAiciIKdmFsdWUgPSAiMS8o"
    "MSAtIDIqTS9yKSIKCltbY2hhcnQubWV0cmljXV0KaSA9ICJ0aGV0YSIKaiA9ICJ0aGV0"
    "YSIKdmFsdWUgPSAicl4yIgoKW1tjaGFydC5tZXRyaWNdXQppID0gInBoaSIKaiA9ICJw"
    "aGkiCnZhbHVlID0gInJeMipzaW4odGhldGEpXjIiCgpbcHJvdmVuYW5jZV0Kc291cmNl"
    "X2tpbmQgPSAic2Vjb25kYXJ5IgpjaXRhdGlvbiA9ICJ0byBiZSBmaWxsZWQgYnkgaXNz"
    "dWUgIzczIgpsb2NhdG9yID0gInRvIGJlIGZpbGxlZCBieSBpc3N1ZSAjNzMiCnRyYW5z"
    "Y3JpYmVkX29uID0gIjIwMjYtMDgtMDciCg=="
)

#: The same second record, carrying the other end of the link.
KERR_SCHILD_SUPERSEDING = (
    "CnNjaGVtYV92ZXJzaW9uID0gIjEiCgppZCA9ICJrZXJyLXNjaGlsZCIKdmVyc2lvbiA9"
    "IDEKc3VwZXJzZWRlcyA9IFsia2VyciJdCm5hbWUgPSAiS2VyciBpbiBLZXJyLVNjaGls"
    "ZCBmb3JtIgpkaW1lbnNpb24gPSA0CnNpZ25hdHVyZSA9ICItKysrIgoKY292ZXJhZ2Vf"
    "YXJndW1lbnQgPSAiT25lIHN0cmF0dW0sIG1hcmtlZCBnZW5lcmljLCB3aG9zZSBjb25k"
    "aXRpb24gaXMgdGhlIGRlY2xhcmVkIHJhbmdlIE0gPiAwIG9mIHRoZSBvbmUgcGFyYW1l"
    "dGVyLiBOb3RoaW5nIGxpZXMgb3V0c2lkZSBpdCwgc28gdGhlIHN0cmF0YSBjb3ZlciB0"
    "aGUgcmFuZ2UuIgoKW1twYXJhbWV0ZXJdXQpuYW1lID0gIk0iCmRvbWFpbiA9ICJyZWFs"
    "IgpyYW5nZSA9ICJNID4gMCIKbWVhbmluZyA9ICJtYXNzIHBhcmFtZXRlciIKClttYXR0"
    "ZXJdCm1vZGVsID0gInZhY3V1bSIKCltbc3RyYXR1bV1dCm5hbWUgPSAiZ2VuZXJpYyIK"
    "Z2VuZXJpYyA9IHRydWUKY29uZGl0aW9uID0gIk0gPiAwIgoKW1tjaGFydF1dCm5hbWUg"
    "PSAiZXh0ZXJpb3IiCmNvb3JkaW5hdGVzID0gWyJ0IiwgInIiLCAidGhldGEiLCAicGhp"
    "Il0KcmVnaW9uID0gInRoZSBzdGF0aWMgcmVnaW9uIG91dHNpZGUgdGhlIGhvcml6b24i"
    "CnJhbmdlID0gWyJyID4gMipNIl0KCltbY2hhcnQubWV0cmljXV0KaSA9ICJ0IgpqID0g"
    "InQiCnZhbHVlID0gIi0oMSAtIDIqTS9yKSIKCltbY2hhcnQubWV0cmljXV0KaSA9ICJy"
    "IgpqID0gInIiCnZhbHVlID0gIjEvKDEgLSAyKk0vcikiCgpbW2NoYXJ0Lm1ldHJpY11d"
    "CmkgPSAidGhldGEiCmogPSAidGhldGEiCnZhbHVlID0gInJeMiIKCltbY2hhcnQubWV0"
    "cmljXV0KaSA9ICJwaGkiCmogPSAicGhpIgp2YWx1ZSA9ICJyXjIqc2luKHRoZXRhKV4y"
    "IgoKW3Byb3ZlbmFuY2VdCnNvdXJjZV9raW5kID0gInNlY29uZGFyeSIKY2l0YXRpb24g"
    "PSAidG8gYmUgZmlsbGVkIGJ5IGlzc3VlICM3MyIKbG9jYXRvciA9ICJ0byBiZSBmaWxs"
    "ZWQgYnkgaXNzdWUgIzczIgp0cmFuc2NyaWJlZF9vbiA9ICIyMDI2LTA4LTA3Igo="
)

#: A third id, which is what two records in two directories look like when
#: they are two entries rather than one id spent twice.
KERR_NEWMAN = (
    "CnNjaGVtYV92ZXJzaW9uID0gIjEiCgppZCA9ICJrZXJyLW5ld21hbiIKdmVyc2lvbiA9"
    "IDEKbmFtZSA9ICJLZXJyLU5ld21hbiIKZGltZW5zaW9uID0gNApzaWduYXR1cmUgPSAi"
    "LSsrKyIKCmNvdmVyYWdlX2FyZ3VtZW50ID0gIk9uZSBzdHJhdHVtLCBtYXJrZWQgZ2Vu"
    "ZXJpYywgd2hvc2UgY29uZGl0aW9uIGlzIHRoZSBkZWNsYXJlZCByYW5nZSBNID4gMCBv"
    "ZiB0aGUgb25lIHBhcmFtZXRlci4gTm90aGluZyBsaWVzIG91dHNpZGUgaXQsIHNvIHRo"
    "ZSBzdHJhdGEgY292ZXIgdGhlIHJhbmdlLiIKCltbcGFyYW1ldGVyXV0KbmFtZSA9ICJN"
    "Igpkb21haW4gPSAicmVhbCIKcmFuZ2UgPSAiTSA+IDAiCm1lYW5pbmcgPSAibWFzcyBw"
    "YXJhbWV0ZXIiCgpbbWF0dGVyXQptb2RlbCA9ICJ2YWN1dW0iCgpbW3N0cmF0dW1dXQpu"
    "YW1lID0gImdlbmVyaWMiCmdlbmVyaWMgPSB0cnVlCmNvbmRpdGlvbiA9ICJNID4gMCIK"
    "CltbY2hhcnRdXQpuYW1lID0gImV4dGVyaW9yIgpjb29yZGluYXRlcyA9IFsidCIsICJy"
    "IiwgInRoZXRhIiwgInBoaSJdCnJlZ2lvbiA9ICJ0aGUgc3RhdGljIHJlZ2lvbiBvdXRz"
    "aWRlIHRoZSBob3Jpem9uIgpyYW5nZSA9IFsiciA+IDIqTSJdCgpbW2NoYXJ0Lm1ldHJp"
    "Y11dCmkgPSAidCIKaiA9ICJ0Igp2YWx1ZSA9ICItKDEgLSAyKk0vcikiCgpbW2NoYXJ0"
    "Lm1ldHJpY11dCmkgPSAiciIKaiA9ICJyIgp2YWx1ZSA9ICIxLygxIC0gMipNL3IpIgoK"
    "W1tjaGFydC5tZXRyaWNdXQppID0gInRoZXRhIgpqID0gInRoZXRhIgp2YWx1ZSA9ICJy"
    "XjIiCgpbW2NoYXJ0Lm1ldHJpY11dCmkgPSAicGhpIgpqID0gInBoaSIKdmFsdWUgPSAi"
    "cl4yKnNpbih0aGV0YSleMiIKCltwcm92ZW5hbmNlXQpzb3VyY2Vfa2luZCA9ICJzZWNv"
    "bmRhcnkiCmNpdGF0aW9uID0gInRvIGJlIGZpbGxlZCBieSBpc3N1ZSAjNzMiCmxvY2F0"
    "b3IgPSAidG8gYmUgZmlsbGVkIGJ5IGlzc3VlICM3MyIKdHJhbnNjcmliZWRfb24gPSAi"
    "MjAyNi0wOC0wNyIK"
)

#: ``kerr`` at version 2, with the one correction entry that version owes.
KERR_AT_TWO = (
    "CnNjaGVtYV92ZXJzaW9uID0gIjEiCgppZCA9ICJrZXJyIgp2ZXJzaW9uID0gMgpjb3Jy"
    "ZWN0aW9uID0gWwogIHsgdmVyc2lvbiA9IDIsIGRhdGUgPSAiMjAyNi0wOC0wOSIsIHJl"
    "YXNvbiA9ICJ0aGUgY2xhaW1lZCBQZXRyb3YgdHlwZSB3YXMgcmVhZCBvZmYgdGhlIHdy"
    "b25nIGxpbmUiIH0sCl0KbmFtZSA9ICJLZXJyIgpkaW1lbnNpb24gPSA0CnNpZ25hdHVy"
    "ZSA9ICItKysrIgoKY292ZXJhZ2VfYXJndW1lbnQgPSAiT25lIHN0cmF0dW0sIG1hcmtl"
    "ZCBnZW5lcmljLCB3aG9zZSBjb25kaXRpb24gaXMgdGhlIGRlY2xhcmVkIHJhbmdlIE0g"
    "PiAwIG9mIHRoZSBvbmUgcGFyYW1ldGVyLiBOb3RoaW5nIGxpZXMgb3V0c2lkZSBpdCwg"
    "c28gdGhlIHN0cmF0YSBjb3ZlciB0aGUgcmFuZ2UuIgoKW1twYXJhbWV0ZXJdXQpuYW1l"
    "ID0gIk0iCmRvbWFpbiA9ICJyZWFsIgpyYW5nZSA9ICJNID4gMCIKbWVhbmluZyA9ICJt"
    "YXNzIHBhcmFtZXRlciIKClttYXR0ZXJdCm1vZGVsID0gInZhY3V1bSIKCltbc3RyYXR1"
    "bV1dCm5hbWUgPSAiZ2VuZXJpYyIKZ2VuZXJpYyA9IHRydWUKY29uZGl0aW9uID0gIk0g"
    "PiAwIgoKW1tjaGFydF1dCm5hbWUgPSAiZXh0ZXJpb3IiCmNvb3JkaW5hdGVzID0gWyJ0"
    "IiwgInIiLCAidGhldGEiLCAicGhpIl0KcmVnaW9uID0gInRoZSBzdGF0aWMgcmVnaW9u"
    "IG91dHNpZGUgdGhlIGhvcml6b24iCnJhbmdlID0gWyJyID4gMipNIl0KCltbY2hhcnQu"
    "bWV0cmljXV0KaSA9ICJ0IgpqID0gInQiCnZhbHVlID0gIi0oMSAtIDIqTS9yKSIKCltb"
    "Y2hhcnQubWV0cmljXV0KaSA9ICJyIgpqID0gInIiCnZhbHVlID0gIjEvKDEgLSAyKk0v"
    "cikiCgpbW2NoYXJ0Lm1ldHJpY11dCmkgPSAidGhldGEiCmogPSAidGhldGEiCnZhbHVl"
    "ID0gInJeMiIKCltbY2hhcnQubWV0cmljXV0KaSA9ICJwaGkiCmogPSAicGhpIgp2YWx1"
    "ZSA9ICJyXjIqc2luKHRoZXRhKV4yIgoKW3Byb3ZlbmFuY2VdCnNvdXJjZV9raW5kID0g"
    "InNlY29uZGFyeSIKY2l0YXRpb24gPSAidG8gYmUgZmlsbGVkIGJ5IGlzc3VlICM3MyIK"
    "bG9jYXRvciA9ICJ0byBiZSBmaWxsZWQgYnkgaXNzdWUgIzczIgp0cmFuc2NyaWJlZF9v"
    "biA9ICIyMDI2LTA4LTA3Igo="
)

#: ``kerr`` at version 3, with both entries, which is what record 0004
#: requires: the list runs from 2 up to the record's own version.
KERR_AT_THREE = (
    "CnNjaGVtYV92ZXJzaW9uID0gIjEiCgppZCA9ICJrZXJyIgp2ZXJzaW9uID0gMwpjb3Jy"
    "ZWN0aW9uID0gWwogIHsgdmVyc2lvbiA9IDIsIGRhdGUgPSAiMjAyNi0wOC0wOSIsIHJl"
    "YXNvbiA9ICJ0aGUgY2xhaW1lZCBQZXRyb3YgdHlwZSB3YXMgcmVhZCBvZmYgdGhlIHdy"
    "b25nIGxpbmUiIH0sCiAgeyB2ZXJzaW9uID0gMywgZGF0ZSA9ICIyMDI2LTA4LTEwIiwg"
    "cmVhc29uID0gInRoZSBkZWNsYXJlZCBtYXNzIHJhbmdlIGV4Y2x1ZGVkIHRoZSBleHRy"
    "ZW1hbCBjYXNlIiB9LApdCm5hbWUgPSAiS2VyciIKZGltZW5zaW9uID0gNApzaWduYXR1"
    "cmUgPSAiLSsrKyIKCmNvdmVyYWdlX2FyZ3VtZW50ID0gIk9uZSBzdHJhdHVtLCBtYXJr"
    "ZWQgZ2VuZXJpYywgd2hvc2UgY29uZGl0aW9uIGlzIHRoZSBkZWNsYXJlZCByYW5nZSBN"
    "ID4gMCBvZiB0aGUgb25lIHBhcmFtZXRlci4gTm90aGluZyBsaWVzIG91dHNpZGUgaXQs"
    "IHNvIHRoZSBzdHJhdGEgY292ZXIgdGhlIHJhbmdlLiIKCltbcGFyYW1ldGVyXV0KbmFt"
    "ZSA9ICJNIgpkb21haW4gPSAicmVhbCIKcmFuZ2UgPSAiTSA+IDAiCm1lYW5pbmcgPSAi"
    "bWFzcyBwYXJhbWV0ZXIiCgpbbWF0dGVyXQptb2RlbCA9ICJ2YWN1dW0iCgpbW3N0cmF0"
    "dW1dXQpuYW1lID0gImdlbmVyaWMiCmdlbmVyaWMgPSB0cnVlCmNvbmRpdGlvbiA9ICJN"
    "ID4gMCIKCltbY2hhcnRdXQpuYW1lID0gImV4dGVyaW9yIgpjb29yZGluYXRlcyA9IFsi"
    "dCIsICJyIiwgInRoZXRhIiwgInBoaSJdCnJlZ2lvbiA9ICJ0aGUgc3RhdGljIHJlZ2lv"
    "biBvdXRzaWRlIHRoZSBob3Jpem9uIgpyYW5nZSA9IFsiciA+IDIqTSJdCgpbW2NoYXJ0"
    "Lm1ldHJpY11dCmkgPSAidCIKaiA9ICJ0Igp2YWx1ZSA9ICItKDEgLSAyKk0vcikiCgpb"
    "W2NoYXJ0Lm1ldHJpY11dCmkgPSAiciIKaiA9ICJyIgp2YWx1ZSA9ICIxLygxIC0gMipN"
    "L3IpIgoKW1tjaGFydC5tZXRyaWNdXQppID0gInRoZXRhIgpqID0gInRoZXRhIgp2YWx1"
    "ZSA9ICJyXjIiCgpbW2NoYXJ0Lm1ldHJpY11dCmkgPSAicGhpIgpqID0gInBoaSIKdmFs"
    "dWUgPSAicl4yKnNpbih0aGV0YSleMiIKCltwcm92ZW5hbmNlXQpzb3VyY2Vfa2luZCA9"
    "ICJzZWNvbmRhcnkiCmNpdGF0aW9uID0gInRvIGJlIGZpbGxlZCBieSBpc3N1ZSAjNzMi"
    "CmxvY2F0b3IgPSAidG8gYmUgZmlsbGVkIGJ5IGlzc3VlICM3MyIKdHJhbnNjcmliZWRf"
    "b24gPSAiMjAyNi0wOC0wNyIK"
)

#: The same record with the entry for version 2 missing, which is the
#: correction nobody is told about.
KERR_AT_THREE_MISSING_TWO = (
    "CnNjaGVtYV92ZXJzaW9uID0gIjEiCgppZCA9ICJrZXJyIgp2ZXJzaW9uID0gMwpjb3Jy"
    "ZWN0aW9uID0gWwogIHsgdmVyc2lvbiA9IDMsIGRhdGUgPSAiMjAyNi0wOC0xMCIsIHJl"
    "YXNvbiA9ICJ0aGUgZGVjbGFyZWQgbWFzcyByYW5nZSBleGNsdWRlZCB0aGUgZXh0cmVt"
    "YWwgY2FzZSIgfSwKXQpuYW1lID0gIktlcnIiCmRpbWVuc2lvbiA9IDQKc2lnbmF0dXJl"
    "ID0gIi0rKysiCgpjb3ZlcmFnZV9hcmd1bWVudCA9ICJPbmUgc3RyYXR1bSwgbWFya2Vk"
    "IGdlbmVyaWMsIHdob3NlIGNvbmRpdGlvbiBpcyB0aGUgZGVjbGFyZWQgcmFuZ2UgTSA+"
    "IDAgb2YgdGhlIG9uZSBwYXJhbWV0ZXIuIE5vdGhpbmcgbGllcyBvdXRzaWRlIGl0LCBz"
    "byB0aGUgc3RyYXRhIGNvdmVyIHRoZSByYW5nZS4iCgpbW3BhcmFtZXRlcl1dCm5hbWUg"
    "PSAiTSIKZG9tYWluID0gInJlYWwiCnJhbmdlID0gIk0gPiAwIgptZWFuaW5nID0gIm1h"
    "c3MgcGFyYW1ldGVyIgoKW21hdHRlcl0KbW9kZWwgPSAidmFjdXVtIgoKW1tzdHJhdHVt"
    "XV0KbmFtZSA9ICJnZW5lcmljIgpnZW5lcmljID0gdHJ1ZQpjb25kaXRpb24gPSAiTSA+"
    "IDAiCgpbW2NoYXJ0XV0KbmFtZSA9ICJleHRlcmlvciIKY29vcmRpbmF0ZXMgPSBbInQi"
    "LCAiciIsICJ0aGV0YSIsICJwaGkiXQpyZWdpb24gPSAidGhlIHN0YXRpYyByZWdpb24g"
    "b3V0c2lkZSB0aGUgaG9yaXpvbiIKcmFuZ2UgPSBbInIgPiAyKk0iXQoKW1tjaGFydC5t"
    "ZXRyaWNdXQppID0gInQiCmogPSAidCIKdmFsdWUgPSAiLSgxIC0gMipNL3IpIgoKW1tj"
    "aGFydC5tZXRyaWNdXQppID0gInIiCmogPSAiciIKdmFsdWUgPSAiMS8oMSAtIDIqTS9y"
    "KSIKCltbY2hhcnQubWV0cmljXV0KaSA9ICJ0aGV0YSIKaiA9ICJ0aGV0YSIKdmFsdWUg"
    "PSAicl4yIgoKW1tjaGFydC5tZXRyaWNdXQppID0gInBoaSIKaiA9ICJwaGkiCnZhbHVl"
    "ID0gInJeMipzaW4odGhldGEpXjIiCgpbcHJvdmVuYW5jZV0Kc291cmNlX2tpbmQgPSAi"
    "c2Vjb25kYXJ5IgpjaXRhdGlvbiA9ICJ0byBiZSBmaWxsZWQgYnkgaXNzdWUgIzczIgps"
    "b2NhdG9yID0gInRvIGJlIGZpbGxlZCBieSBpc3N1ZSAjNzMiCnRyYW5zY3JpYmVkX29u"
    "ID0gIjIwMjYtMDgtMDciCg=="
)

FIXTURES: dict[str, Fixture] = {
    # id-carried-by-two-records: one id under two paths. A flat directory
    # cannot produce this, because the filesystem refuses two files with one
    # name, so the fixture is what a walk that descends meets.
    "id-carried-by-two-records": Fixture(
        refused=Half(
            documents=(("rotating/kerr.toml", KERR), ("charged/kerr.toml", KERR)),
        ),
        accepted=Half(
            documents=(
                ("rotating/kerr.toml", KERR),
                ("charged/kerr-newman.toml", KERR_NEWMAN),
            ),
        ),
        note=(
            "the second record spends its own id rather than the first one's, "
            "which is the difference between two entries in two directories and "
            "one entry written twice"
        ),
    ),
    # supersession-names-no-record: the successor is not in the catalogue.
    "supersession-names-no-record": Fixture(
        refused=Half(documents=(("kerr.toml", KERR_SUPERSEDED),)),
        accepted=Half(
            documents=(
                ("kerr.toml", KERR_SUPERSEDED),
                ("kerr-schild.toml", KERR_SCHILD_SUPERSEDING),
            ),
        ),
        note=(
            "the record the supersession names is in the catalogue, which is "
            "the mistake of landing the forward link before the record it "
            "points at"
        ),
    ),
    # half-written-supersession: both records are here and only one of them
    # knows about the other.
    "half-written-supersession": Fixture(
        refused=Half(
            documents=(
                ("kerr.toml", KERR_SUPERSEDED),
                ("kerr-schild.toml", KERR_SCHILD),
            ),
        ),
        accepted=Half(
            documents=(
                ("kerr.toml", KERR_SUPERSEDED),
                ("kerr-schild.toml", KERR_SCHILD_SUPERSEDING),
            ),
        ),
        note=(
            'the successor carries supersedes = ["kerr"], which is the second '
            "end of the link and the line somebody editing one file forgets"
        ),
    ),
    # correction-list-does-not-run-to-the-version: version 3 and one entry.
    "correction-list-does-not-run-to-the-version": Fixture(
        refused=Half(documents=(("kerr.toml", KERR_AT_THREE_MISSING_TWO),)),
        accepted=Half(documents=(("kerr.toml", KERR_AT_THREE),)),
        note=(
            "the entry for version 2 is in the list, so it runs 2 then 3 rather "
            "than starting at 3, which is the correction a consumer pinned to "
            "version 1 would never be told about"
        ),
    ),
    # unknown-identifier: the records are the same in both halves and the pin
    # is what moves, because this refusal is about what a consumer asked for.
    "unknown-identifier": Fixture(
        refused=Half(documents=(("kerr.toml", KERR),), pin=("kerr-newman", 1)),
        accepted=Half(documents=(("kerr.toml", KERR),), pin=("kerr", 1)),
        note=(
            "the pin names an id this catalogue holds, one hyphenated word away "
            "from one it does not"
        ),
    ),
}

#: The pair the correction report is read off, which is not a refusal and so is
#: not a fixture above. A consumer pinned to version 1 meeting version 2.
CORRECTED = Half(documents=(("kerr.toml", KERR_AT_TWO),), pin=("kerr", 1))
