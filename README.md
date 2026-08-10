# raumbuch

The equivalence problem, whether two spacetimes are the same up to coordinates, is solved in theory and in practice through Cartan, Brans and Karlhede, and implemented in CLASSI, an extension of the LISP-based SHEEP from the nineteen-seventies. A 2001 plan to make a database of over 200 classified solutions accessible and updatable never became infrastructure, and the reference remains a book with hundreds of solutions on paper. It is not historical: a 2023 teleparallel gravity paper states it is hard to distinguish a new solution from a known one, so people may be publishing known results in new coordinates. Each solution becomes an object with metric, coordinate range, parameters, stress-energy tensor, Petrov type and Killing vectors, and the deliverable is one callable function, is_this_new(metric).

## What a positive answer means, and what it does not

A positive answer means the two metrics are locally isometric. On some
neighbourhood of each, there is a coordinate change carrying one metric to the
other exactly, and the answer names the invariants that agree and, where it can
be produced, the frame that realises the match. It is a statement about the
geometry of a neighbourhood and about nothing larger.

A positive answer does not say the two spacetimes are the same manifold, that
either is the maximal extension of the other, that a singularity in one chart is
physical, that the two carry the same matter interpretation, or that either
metric is correct. The algorithm never sees the topology, the extension or the
physics; it reads local invariants and it is silent about everything that is not
one.

Both paragraphs are quoted from
[docs/decisions/0007-what-same-means.md](docs/decisions/0007-what-same-means.md),
where the relation they describe is argued. The `documents` leg of the gate
compares them against that record byte for byte, so a copy that has drifted into
something more reassuring is refused rather than published.

## The network, and the personal data this project holds

This software makes no network connection. It sends no telemetry, checks for no
updates, fetches no catalogue and contacts nothing at import time or on a first
run. A catalogue is a directory of files already on your machine, and
classifying a metric is arithmetic performed on it. The personal data this
project holds is what a record's citation and prose fields say about the people
credited in them, and what your own file paths and machine names reveal about
you if you copy a log somewhere public. None of it leaves your machine, because
nothing here transmits anything. Fetching dependencies when you install or
build the software is your package manager's connection and not this
software's.

Quoted from
[docs/decisions/0014-network-and-personal-data.md](docs/decisions/0014-network-and-personal-data.md),
and compared against it by the same leg. What is refused by a check and what is
not is written in that record rather than summarised here, and the two are not
the same statement.

Planning happens on the issue tracker first. Every decision that shapes
the architecture is written down there with its reasons before the code
that depends on it exists.

See [NOTICE.md](NOTICE.md) for the intended-use notice.

## License

AGPL-3.0, the GNU Affero General Public License version 3. Copyright (C) 2026 Nils Lehnen.

See [LICENSE](LICENSE) for the full terms.
