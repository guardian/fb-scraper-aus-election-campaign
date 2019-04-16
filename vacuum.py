#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

con = sqlite3.connect("scraperwiki.sqlite")

con.execute("VACUUM")
con.close()