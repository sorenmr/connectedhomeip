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
ThreeLevelAutoEnum = Clusters.ClosureDimension.Enums.ThreeLevelAutoEnum 

class TC_CLDIM_3_3(MatterBaseTest):
    def __init__(self, *args):
        super().__init__(*args)
        self.endpoint = 0

    def steps_TC_CLDIM_3_3(self) -> list[TestStep]:
        steps = [
            TestStep(1, "Commissioning, already done", is_commissioning=True),
            TestStep(2, "Send Step command"),
            TestStep(3, "Wait for motion"),
            TestStep(4, "Read CurrentPositioning attribute"),
            TestStep(5, "Send Step command"),
            TestStep(6, "Read TargetPositioning attribute"),
            TestStep(7, "Wait for motion"),
            TestStep(8, "Read CurrentPositioning attribute"),
         ]
        return steps
    
    async def read_attribute_expect_success(self, endpoint, attribute):
        cluster = Clusters.Objects.ClosureDimension
        return await self.read_single_attribute_check_success(endpoint=endpoint, cluster=cluster, attribute=attribute)

    async def wait_for_motion(self, duration_s):
        logging.info("Test will now wait for {duration_s} seconds")
        time.sleep(duration_s)

    def pics_TC_CLDIM_3_3(self) -> list[str]:
        return ["CLDIM.S.F00"]

    @async_test_body
    async def test_TC_CLDIM_3_3(self):
        is_ci = self.check_pics("PICS_SDK_CI_ONLY")

        StepMotionDuration = self.matter_test_config.global_test_params['PIXIT.CLDIM.StepMotionDuration']

        self.endpoint = self.matter_test_config.endpoint
        
        attributes = Clusters.ClosureDimension.Attributes

        #STEP 1: Commission DUT to TH (can be skipped if done in a preceding test)
        self.step(1)

        #STEP 2: Send Step command
        self.step(2)
        await self.send_single_cmd(cmd=Clusters.Objects.ClosureDimension.Commands.Step(Direction=StepDirectionEnum.TowardsMax, NumberOfSteps=1), endpoint=self.endpoint)

        #STEP 3: Wait for motion
        self.step(3)
        wait_for_motion(self, StepMotionDuration)

        #STEP 4: Read CurrentPositioning attribute
        self.step(4)
        currentPositioning = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.CurrentPositioning)

        #Validate values
        asserts.assert_in(currentPositioning.Position, range(0, 10000), "Value is out of range")

        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            asserts.assert_not_equal(currentPositioning.Speed, ThreeLevelAutoEnum.Auto, "Unexpected value")
        else:
            asserts.assert_equal(currentPositioning.Speed, ThreeLevelAutoEnum.Auto, "Unexpected value")

        StartPosition = currentPositioning.Position

        #STEP 5: Send Step command
        self.step(5)
        await self.send_single_cmd(cmd=Clusters.Objects.ClosureDimension.Commands.Step(Direction=StepDirectionEnum.TowardsMin, NumberOfSteps=0), endpoint=self.endpoint)

        #STEP 6: Read TargetPositioning attribute
        self.step(6)
        targetPosition = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.TargetPositioning)

        #Validate values
        asserts.assert_equal(targetPositioning.Position, StartPosition, "Unexpected value")

        #STEP 7: Wait for motion
        self.step(7)
        wait_for_motion(self, StepMotionDuration)

        #STEP 8: Read CurrentPositioning attribute
        self.step(8)
        currentPositioning = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.CurrentPositioning)

        #Validate values
        asserts.assert_equal(currentPositioning.Position, StartPosition, "Unexpected value")

if __name__ == "__main__":
    default_matter_test_main()
