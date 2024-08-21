# Track Time

Track your time spent on various projects.
Start a timer and when you're finished enter the project name and the time taken will be saved.

## Environment Setup 
The run environment is managed by poetry. 
Set up the environment with 
```
poetry shell
poetry install
```
### Development
Install the development environment with
```
poetry install --with dev
```
lint with
```
poetry run scripts/lint
```

## TODO
* [ ] Dmenu/sxhkd start and stop
* [ ] Daemon process that can be started and stopped
* [ ] Integrate with panel bar
* [ ] Android app 
* [-] Add additional flags (meeting, travel, light) 
* [-] Plot additional flags (meeting, travel, light) 
* [ ] Use group and project name constancy (a project is part of a group)
* [ ] Monthly usage panel (are you on track to hit averages)
* [ ] General clean up of code with comments
* [x] Use proper date strings
* [x] Put into python setup tools package
* [ ] Extra column for the specifics of what was being done
* [x] Change to be based around new `tt -u` usage
* [ ] Make service to go through data and pick out input errors
