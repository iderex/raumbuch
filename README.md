# raumbuch

The equivalence problem, whether two spacetimes are the same up to coordinates, is solved in theory and in practice through Cartan, Brans and Karlhede, and implemented in CLASSI, an extension of the LISP-based SHEEP from the nineteen-seventies. A 2001 plan to make a database of over 200 classified solutions accessible and updatable never became infrastructure, and the reference remains a book with hundreds of solutions on paper. It is not historical: a 2023 teleparallel gravity paper states it is hard to distinguish a new solution from a known one, so people may be publishing known results in new coordinates. Each solution becomes an object with metric, coordinate range, parameters, stress-energy tensor, Petrov type and Killing vectors, and the deliverable is one callable function, is_this_new(metric).

Planning happens on the issue tracker first. Every decision that shapes
the architecture is written down there with its reasons before the code
that depends on it exists.

See [NOTICE.md](NOTICE.md) for the intended-use notice.

## License

AGPL-3.0, the GNU Affero General Public License version 3. Copyright (C) 2026 Nils Lehnen.

See [LICENSE](LICENSE) for the full terms.
