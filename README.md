# fedown

Small script written in Python that prints [Fedora](https://getfedora.org) user access information parsed from the [Fedora Pagure API](https://src.fedoraproject.org/api/).
Licensed under [GPLv3](http://www.gnu.org/licenses/gpl.txt).

[![Copr build status](https://copr.fedorainfracloud.org/coprs/panovotn/fedown/package/fedown/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/panovotn/fedown/package/fedown/)

## Contents

* [Installation](#installation)
    - [Copr](#copr)
    - [Manual](#manual)
* [Usage](#usage)
    - [Repository query](#repository-query)
        - [Basic](#basic)
        - [Types](#types)
        - [Namespaces](#namespaces)
        - [Examples](#examples)
    - [User query](#user-query)
      - [Namespaces](#namespaces-1)
      - [Parameters](#parameters)
      - [Examples](#examples-1)
    - [Output format](#output-format)
      - [Human readable](#human-readable)
      - [Colors](#colors)
    - [Flow control](#flow-control)
      - [Skip on failure](#skip-on-failure)
* [Recommended aliases](#recommended-aliases)

## Installation

There is only Copr and manual installation process available at the moment.

---

### Copr

 * For Fedora you can use [Copr](https://copr.fedorainfracloud.org/) builds.

```
# dnf copr enable panovotn/fedown
# dnf install fedown
```

 * See the [Copr repository](https://copr.fedorainfracloud.org/coprs/panovotn/fedown/) for more information.

### Manual

 * The `~/.local/bin` directory needs to be included in your `PATH` environment variable or replaced with one that is.

```
$ git clone https://github.com/UncleAlbie/fedown.git
$ cd fedown
$ cp fedown/fedown.py ~/.local/bin/fedown
$ chmod +x ~/.local/bin/fedown
```

---

## Usage

To show the usage screen use parameter `-h` or `--help`.

```
$ fedown -h
```

---

### Repository query

Use `fedown` to query information for given repositories.

---

#### Basic

 * With no extra parameters, `fedown` prints owner for each given repository. The default namespace is `rpms`.

```
$ fedown REPOSITORY [REPOSITORY..]
```

---

#### Types

 * For different Pagure access types use parameter `-t` or `--type` to specify the type. 

 * Available types:
    - `owner` query for owner access type
    - `admin` query for admin access type
    - `commit` query for commit access type
    - `all` query for all access types above

```
$ fedown -t TYPE REPOSITORY [REPOSITORY..]
```

---

#### Namespaces

 * To query different namespace use parameter `-n` or `--namespace` to specify the namespace.

 * Available namespaces:
    - `rpms` query for rpms namespace
    - `modules` query for modules namespace
    - `containers` query for containers namespace
    - `tests` query for tests namespace

 * There is one special namespace `users` which behaves differently from the namespaces above. See [user query](#user-query) for more information.

```
$ fedown -n NAMESPACE REPOSITORY [REPOSITORY..]
```

---

#### Examples:

 * Replace `fakerepo` with existing repository name.

```
$ fedown fakerepo
fakeowner
```

```
$ fedown -n tests -t admin fakerepo
fakeadmin01
fakeadmin02
fakeadmin03
```

---

### User query

Use `fedown` to query information for given users.

---

#### Namespaces

 * To query access information for given users use parameter `-n` or `--namespace` to specify the `users` namespace.

```
$ fedown -n users USERNAME [USERNAME..]
```

---

#### Parameters

 * For other access type control use the `-t` or `--type` parameter the same way as with repo queries.

```
$ fedown -n users -t admin USERNAME [USERNAME..]
```

 * Option parameter `-F` or `--include-forks` can be used to include forks in the listing.

 * Option parameter `-N` or `--names-only` can be used to exclude repository namespace prefix from listing.

---

#### Examples:

 * Replace `fakeuser` with existing username.

```
$ fedown -n users fakeuser
rpms/fakerepo02
```

```
$ fedown -n users -F fakeuser
rpms/fakerepo02
forks/fakeuser/fakerepo01
forks/fakeuser/fakerepo03
```

```
$ fedown -n users -F -N fakeuser
fakerepo02
fakerepo01
fakerepo03
```

```
$ fedown -n users -t admin fakeuser
rpms/fakerepo03
rpms/fakerepo04
tests/fakerepo01
modules/fakerepo01
```

---

### Output format

Some options to control the `fedown` output format are available.

---

#### Human readable

 * Option parameter `-H` or `--human-readable` can be used to enable human readable ouput format.

 ```
$ fedown -H REPOSITORY [REPOSITORY..]
 ```

---

#### Colors

 * Option parameter `-C` or `--colors` can be used to enable colors (only works with `-H` or `--human-readable`).

 ```
$ fedown -H -C REPOSITORY [REPOSITORY..]
 ```

---

### Flow control

Some options to control the `fedown` behaviour are available.

---

#### Skip on failure

 * By default `fedown` quits on Pagure API request failure and prints error message to `stderr`.
 * Option parameter `-S` or `--skip-on-failure` can be used to prevent quitting on Pagure API request failure.

```
$ fedown -S REPOSITORY [REPOSITORY..]
```

---

## Recommended aliases

Recommended Bash aliases.

---

 * Basic repository queries.

```bash
alias fo='fedown -S'
alias fousers='fedown -Sn users'
```

---

 * Basic repository queries (colored human readable).

```bash
alias foh='fedown -SHC'
alias fohusers='fedown -SHCFn users'
```

---

 * Query all information in human readable format.

```bash
alias foall='fedown -SHCt all'
alias foallusers='fedown -SHCFt all -n users'
```

---

 * Repository owner query for requires based on `$PWD`.

    - Requires current working directory name to be a rpms repository name<br>(eg. `~/sources/pagure/fedora/rpms/fakerepo` for `fakerepo` query).
    - Works with the `rpms` namespace.
    - Output format: `repository: owner`
    - For requires in `rawhide` add `--repo=rawhide` option argument to the `dnf` command bellow.

```bash
alias forequires='for dep in $(dnf -q repoquery --whatrequires ${PWD##*/} --qf "%{source_name}" | uniq); do echo "${dep}: $(fedown ${dep})"; done'
```
