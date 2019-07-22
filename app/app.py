#!/usr/bin/env python
# -*- coding=utf-8 -*-

import connexion
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")

app = connexion.App(__name__, specification_dir='swagger/')
app.add_api("swagger.yml")
try:
    app.run(server='tornado', port=8080)
except KeyboardInterrupt:
    print("bye!")
    sys.exit(0)
