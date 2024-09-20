# Copyright (C) 2020-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

import click
import sys
from pprint import pprint, pformat

from root import app


@app.cli.command("test")
@click.option('--verbose', is_flag=True, default=False)
def resolve_student_names(verbose):
    print("This is only a test")
