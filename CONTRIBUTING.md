# Contributing

Proofstone is in planning, and its plan is the [README](README.md). Changes land on `main` only
through pull requests, squash-merged, with the pull request's title and body as the commit.

## Once per clone

Turn on the git hooks:

```sh
git config core.hooksPath .githooks
```

The pre-commit hook runs `scripts/check_private.py`, which keeps the owner's private research out
of this public repository ("Nothing private comes in", in the README's principles). It blocks a
commit that adds a number on the owner's deny-list, a dollar amount beside the owner's accounts,
one of the private research's files, or a data file outside `samples/`, `examples/` or `fixtures/`.
The deny-list lives outside every repository, at `~/.config/strategy-research/denylist.txt`; without
it, the hook skips that check and says so.

Its tests use only the standard library:

```sh
python3 -m unittest discover scripts
```
