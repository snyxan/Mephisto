#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil
import os
import tempfile
import sh
import shlex

from typing import Type, ClassVar, Optional
from mephisto.data_model.test.architect_tester import ArchitectTests
from mephisto.server.architects.local_architect import LocalArchitect

from mephisto.data_model.database import MephistoDB
from mephisto.data_model.architect import Architect
from mephisto.data_model.assignment_state import AssignmentState
from mephisto.server.blueprints.mock.mock_blueprint import MockBlueprint
from mephisto.server.blueprints.mock.mock_task_builder import MockTaskBuilder
from mephisto.server.blueprints.mock.mock_task_runner import MockTaskRunner


class LocalArchitectTests(ArchitectTests):
    """
    Runs architect tests on the mock class. Tests the general architect interface is
    still working properly, and that the tests are correctly operating.
    """

    ArchitectClass: Type[Architect] = LocalArchitect
    db: MephistoDB
    data_dir: str
    build_dir: str
    curr_architect: Optional[LocalArchitect] = None

    def get_architect(self) -> LocalArchitect:
        """We need to specify that the architect is launching on localhost for testing"""
        opts = {"hostname": "http://localhost", "port": "3000"}
        self.curr_architect = LocalArchitect(
            self.db, opts, self.task_run, self.build_dir
        )
        return self.curr_architect

    def server_is_prepared(self, build_dir: str) -> bool:
        """Ensure the build directory exists"""
        return os.path.exists(os.path.join(build_dir, "router"))

    def server_is_cleaned(self, build_dir: str) -> bool:
        """Ensure the build directory is gone"""
        return not os.path.exists(os.path.join(build_dir, "router"))

    def server_is_shutdown(self) -> bool:
        """Ensure process is no longer running"""
        assert self.curr_architect is not None, "No architect to check"
        return self.curr_architect.server_process.returncode is not None

    # TODO maybe a test where we need to re-instance an architect?

    def tearDown(self) -> None:
        """Overrides teardown to remove server dir"""
        super().tearDown()
        if self.curr_architect is not None:
            if self.curr_architect.running_dir is not None:
                sh.rm(shlex.split("-rf " + self.curr_architect.running_dir))
            if (
                self.curr_architect.server_process is not None
                and not self.server_is_shutdown()
            ):
                self.curr_architect.server_process.terminate()
                self.curr_architect.server_process.wait()


if __name__ == "__main__":
    unittest.main()
