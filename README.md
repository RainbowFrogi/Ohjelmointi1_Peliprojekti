# Welcome to the TOWER DEFENSE game!

**Tower defense** is a game made with pygame by 4 school students at *Metropolia UAS*.

The purpose of this document is to explain how to install some packages and software so that the game runs without a problem.

---
## 1. [#](#INSTALLATIONS) Installations *(REQUIRED)*

### 1.1 [#](#pygame-installations) pygame installation
**pygame** is a light weight game engine.

Before you start the game you will need to study the following packages
using pip or py terminal commands:
```bash
py install pygame
py install pygame_textinput
```
or
```bash
pip install pygame
pip install pygame_textinput
```
## 1.2 [#](#mysql-connector) MySQL Connector
The game will need the *mysql/connector* for connecting to the **MariaDB** using **MySQL Connector**.
You can install the connector that comes with the driver using the following command:
```bash
pip install mysqlx-connector-python
```
or 
follow the instructions from **mysql page**:
``https://dev.mysql.com/doc/dev/connector-python/latest/installation.html``

---
## 2. [#](#MARIADB) MariaDB Set Up
**MariaDB** is an *Relational Database Management System*.


### 2.1 [#](#install-database) Install Database
To install **MariaDB** on **Windows 10** follow this videos:
``https://www.youtube.com/watch?v=-ARMty_N0RU``

### 2.2 [#](#create-user) Create a user
For the purpose of convinience we will create a user with the following parameters.

**Username:** ``'TDUser'@'Localhost'``
**Password:** ``'1234'``

This would be the Query needed to **create the user** in **MariaDB**
```sql
CREATE USER 'TDuser'@'localhost' IDENTIFIED BY '1234';
```

### 2.3 [#](#database-script) Run the database creation script

if you use **MySQL Client** then run this Query:
```sql
SOURCE C:\{absolute-file-path}\towerdefense.sql
```
Change the ``{absolute-file-path}`` with the right path to your ``towerdefense.sql`` file.
**_NOTE:_** search on google "Absolute file path" if you don't know what it means
