#
#    Copyright (c) 2023 Project CHIP Authors
#    All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

# === BEGIN CI TEST ARGUMENTS ===
# test-runner-runs:
#   run1:
#     app: ${ALL_CLUSTERS_APP}
#     app-args: --discriminator 1234 --KVS kvs1 --trace-to json:${TRACE_APP}.json
#     script-args: >
#       --storage-path admin_storage.json
#       --commissioning-method on-network
#       --discriminator 1234
#       --passcode 20202021
#       --trace-to json:${TRACE_TEST_JSON}.json
#       --trace-to perfetto:${TRACE_TEST_PERFETTO}.perfetto
#     factory-reset: true
#     quiet: true
# === END CI TEST ARGUMENTS ===

import logging
from random import choice

import chip.clusters as Clusters
from chip.interaction_model import Status
from chip.testing.matter_testing import MatterBaseTest, TestStep, async_test_body, default_matter_test_main
from mobly import asserts

# ==========================
# Enums
# ==========================

StepDirectionEnum = Clusters.ClosureDimension.Enums.StepDirectionEnum

class TC_CLDIM_3_5(MatterBaseTest):
    def __init__(self, *args):
        super().__init__(*args)
        self.endpoint = 0

    def steps_TC_CLDIM_3_5(self) -> list[TestStep]:
        steps = [
            TestStep(1, "Commissioning, already done", is_commissioning=True),
            TestStep(2, "TH sends Step command to DUT, with Direction=Invalid(2) and NumberOfSteps=1"),
            TestStep(3, "TH sends Step command to DUT, with Direction=TowardsMax, NumberOfSteps=1 and speed=Invalid(4)"),
         ]
        return steps
    
    def pics_TC_CLDIM_3_5(self) -> list[str]:
        return ["CLDIM.S.F00"]

    @async_test_body
    async def test_TC_CLDIM_3_5(self):
        is_ci = self.check_pics("PICS_SDK_CI_ONLY")

        FullMotionDuration = self.matter_test_config.global_test_params['PIXIT.CLDIM.FullMotionDuration']
        StepMotionDuration = self.matter_test_config.global_test_params['PIXIT.CLDIM.StepMotionDuration']

        self.endpoint = self.matter_test_config.endpoint
        
        # STEP 1: Commission DUT to TH (can be skipped if done in a preceding test)
        self.step(1)

        # STEP 2: Read StepValue attribute
        self.step(2)
        result = await self.send_single_cmd(cmd=Clusters.Objects.ClosureDimension.Commands.Step(Direction=2, NumberOfSteps=1), endpoint=self.endpoint)
        asserts.assert_equal(result[0].Status, Status.ConstraintError, "Command did not return CONSTRAINT_ERROR")

        # STEP 3: Read StepValue attribute
        self.step(3)
        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            result = await self.send_single_cmd(cmd=Clusters.Objects.ClosureDimension.Commands.Step(Direction=StepDirectionEnum.TowardsMax, NumberOfSteps=1, Speed=4), endpoint=self.endpoint)
            asserts.assert_equal(result[0].Status, Status.ConstraintError, "Command did not return CONSTRAINT_ERROR")

if __name__ == "__main__":
    default_matter_test_main()
