# TruBe Command Line Tool
Command line tool for partner to work with TruBe REST API.
Valid credentials are needed in order to make requests.
This tool is very helpful and provides a number of essentials command
of Partner APP without installing it. 😁

## Installation

Clone the repository and run the `python propose.py` command:

```bash
$ git clone git@github.com:ronar/trubeapp-command-line-tool.git
$ cd trubeapp-command-line-tool
$ python propose.py
```

For help provide the `-h` or `--help` flag:

```bash
$ python propose.py -h
```

And that's it! Default user and password could be added for more convinient way working with the program.


## Requirements

None


## Commands

`-h, --help`            show this help message and exit  
`-w, --wipe`            wipe all partner auth info  
`-v, --verbose`         increase output verbosity  
`-u USER, --user USER`  
`--password PASSWORD`  
`-l, --list-bookings` | prints list of bookings  
`-p PROPOSE, --propose PROPOSE` | partner proposes for booking  
`-s START_SESSION, --start-session START_SESSION` | partner starts a session  
`-c CONCLUDE_SESSION, --conclude-session CONCLUDE_SESSION` | partner concludes a session  
`-d DECLINE_SESSION, --decline-session DECLINE_SESSION` | partner declines a booking  
`-t TRAINER_DECLINING, --trainer-declining TRAINER_DECLINING` | partner declines a direct booking  
`-r REJECT, --reject REJECT` | partner rejects an assigned session  


## License

```
    TruBe Command Line Tool
    Copyright (C) 2017  Vladimir Shishlyannikov

                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.
```

See the [LICENSE](LICENSE) file for more details.

