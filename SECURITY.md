# Security policy

## Where to send a report

Open a private security advisory:

https://github.com/iderex/raumbuch/security/advisories/new

That form is private to you and the maintainer. Please use it instead of the
public issue tracker for anything that could be exploited before it is fixed.

If the form is unavailable to you for any reason, open a public issue that says
only that you have a security report and asks for a private channel. Do not put
the details in it.

## What this project is, and what it will be

The repository currently holds decision records and workflow files. There is no
library, no command-line tool and no release:

    git ls-files
    gh api repos/iderex/raumbuch/releases --jq 'length'

So the surfaces described below are the ones this document exists to route
reports about, and most of them are not built yet. A report about the
repository's own workflows or configuration is in scope today and is the kind of
report that is actually possible right now.

## In scope

The record loader, once it exists. A catalogue is a directory of files, and those
files come from other people. Anything that makes loading a record do more than
parse it belongs here.

The expression sub-language and its parser. A metric component, a coordinate
range and a parameter range are all strings in a small expression language. If
that parser can be made to reach past its grammar, the consequence is code
execution on the machine of whoever loaded a catalogue, and that is the report
this document is mostly for. A record is designed to be parsed into a syntax
tree and never evaluated as source in any language, so any route from a record to
execution is a defect and not a configuration mistake.

Denial of service that is not the declared cost ceiling. This software is
expected to use large amounts of memory on hard entries and to refuse when it
reaches a declared budget. A crafted record that exhausts a machine long before
that budget, or that makes the refusal itself fail, is in scope. An honest
classification that is simply expensive is not.

Path handling. A record naming a file, a catalogue directory walk, or an output
path that escapes where the operator pointed it.

The repository's own automation. The workflow files in `.github/workflows`, their
permissions, and the way they handle values that come from a pull request.

Anything that causes this software to make a network connection. It is designed to
make none, and one appearing is a defect worth reporting whether or not it is
exploitable.

## Not in scope

A metric that is mathematically wrong. A transcription error, a sign error or a
metric that does not solve what its record claims is a correctness bug. Please
open it on the public issue tracker, where it can be discussed and fixed in the
open. It is important and it is not a vulnerability.

A classification the software could not decide. The library is designed to answer
that it could not decide, with a report of what stopped it. That answer is the
intended behaviour and reporting it as a vulnerability will get a reply saying so.

A wrong classification. Also a correctness bug, also important, also the public
tracker. If a wrong classification is reachable by a record crafted to make it
wrong, that is different and is in scope; say which of the two you mean.

Missing hardening with no reachable consequence, and findings that consist only
of a scanner's output with no path from an input to an effect.

Anything requiring the operator to run a catalogue they already know to be
malicious under privileges they chose to grant. Loading an untrusted catalogue is
a case this project takes seriously, and defeating a defence the operator
deliberately turned off is not.

## What to expect

The maintainer reads reports and will reply. There is no response time promise
here, because this project is not staffed to keep one and a promise nobody keeps
is worse than none. If you have had no reply and want to know whether the report
arrived, ask again on the same advisory.

You will be told which of three things your report is: something that will be
fixed, something that is a correctness bug and belongs on the public tracker, or
something that will not be changed and why.

A fix lands as a public pull request that says what was wrong. Nothing about a
report is published while a fix is being prepared, and nothing is published
afterwards that you asked to keep out.

You will be credited by name in the advisory and in the record of the fix if you
want to be, and not if you do not. Say which.

There is no bounty.

## Supported versions

None yet. There is no release and no tag, so the only thing there is to report
against is the current state of the default branch.

When releases exist, this section will say which of them receive fixes.
