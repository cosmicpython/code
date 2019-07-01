# Example application code for the python architecture book

## Chapters

Each chapter has its own branch which contains all the commits for that chapter,
so it has the state that corresponds to the _end_ of that chapter.  If you want
to try and code along with a chapter, you'll want to check out the branch for the
previous chapter.

https://github.com/python-leap/code/branches/all


## Exercises

Branches for the exercises follow the convention `{chatper_name}_exercise`, eg 
https://github.com/python-leap/code/tree/chapter_03_service_layer_exercise


## Requirements

* docker with docker-compose
* for chapters 1 and 2, and optionally for the rest: a local python3.7 virtualenv


## Building the containers

_(this is only required from chapter 3 onwards)_

```sh
make build
make up
# or
make all # builds, brings containers up, runs tests
```

## Running the tests

```sh
make test
# or, to run individual test types
make unit
make integration
make e2e
# or, if you have a local virtualenv
make up
pytest tests/unit
pytest tests/integration
pytest tests/e2e


## Makefile

There are more useful commands in the makefile, have a look and try them out.

