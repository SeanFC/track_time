# Track Time

Track your time spent on various projects.
State a project and how long you're going to spend on it. 
After the timer finishes you'll be alerted and the time and your time spent on the project will be logged.
Alternatively, start a timer and when you're finished enter the project name and the time taken will be saved

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
* [ ] Change to be based around new `tt -u` usage
