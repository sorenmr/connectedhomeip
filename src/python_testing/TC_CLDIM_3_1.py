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

class TC_CLDIM_3_1(MatterBaseTest):
    def __init__(self, *args):
        super().__init__(*args)
        self.endpoint = 0

    def steps_TC_CLDIM_3_1(self) -> list[TestStep]:
        steps = [
            TestStep(1, "Commissioning, already done", is_commissioning=True),
            TestStep(2, "Read StepValue attribute"),
            TestStep(3, "Read LimitRange attribute"),
            TestStep("4a", "TH sends Steps command to DUT, with Direction=TowardsMax and NumberOfSteps=65536 (0xFF)"),
            TestStep("4b", "Wait for motion"),
            TestStep("4c", "Read CurrentPositioning attribute"),
            TestStep("4d", "Send Steps command"),
            TestStep("4e", "Wait for motion"),
            TestStep("4f", "Read CurrentPositioning attribute"),
            TestStep("5a", "Send Steps command"),
            TestStep("5b", "Read TargetPositioning attribute"),
            TestStep("5c", "Wait for motion"),
            TestStep("5d", "Read CurrentPositioning attribute"),
            TestStep("6a", "Send Steps command"),
            TestStep("6b", "Read TargetPositioning attribute"),
            TestStep("6c", "Wait for motion"),
            TestStep("6d", "Read CurrentPositioning attribute"),
            TestStep("7a", "Send Steps command"),
            TestStep("7b", "Read TargetPositioning attribute"),
            TestStep("7c", "Wait for motion"),
            TestStep("7d", "Read CurrentPositioning attribute"),
            TestStep("8a", "Send Steps command"),
            TestStep("8b", "Read TargetPositioning attribute"),
            TestStep("8c", "Wait for motion"),
            TestStep("8d", "Read CurrentPositioning attribute"),
            TestStep("9a", "Send Steps command"),
            TestStep("9b", "Read TargetPositioning attribute"),
            TestStep("9c", "Wait for motion"),
            TestStep("9d", "Read CurrentPositioning attribute"),
            TestStep("10a", "Send Steps command"),
            TestStep("10b", "Read TargetPositioning attribute"),
            TestStep("10c", "Wait for motion"),
            TestStep("10d", "Read CurrentPositioning attribute"),
         ]
        return steps
    
    async def read_attribute_expect_success(self, endpoint, attribute):
        cluster = Clusters.Objects.ClosureDimension
        return await self.read_single_attribute_check_success(endpoint=endpoint, cluster=cluster, attribute=attribute)

    async def wait_for_motion(self, duration_s):
        logging.info("Test will now wait for {duration_s} seconds")
        time.sleep(duration_s)

    def pics_TC_CLDIM_3_1(self) -> list[str]:
        return ["CLDIM.S.F00"]

    @async_test_body
    async def test_TC_CLDIM_3_1(self):
        is_ci = self.check_pics("PICS_SDK_CI_ONLY")

        FullMotionDuration = self.matter_test_config.global_test_params['PIXIT.CLDIM.FullMotionDuration']
        StepMotionDuration = self.matter_test_config.global_test_params['PIXIT.CLDIM.StepMotionDuration']

        self.endpoint = self.matter_test_config.endpoint
        
        attributes = Clusters.ClosureDimension.Attributes

        MinPosition = 0
        MaxPosition = 10000

        # STEP 1: Commission DUT to TH (can be skipped if done in a preceding test)
        self.step(1)

        # STEP 2: Read StepValue attribute
        self.step(2)
        StepValue = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.StepValue)

        # STEP 3: Read LimitRange attribute
        self.step(3)
        if self.pics_guard(self.check_pics("CLDIM.S.A0006")):
            LimitRange = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.LimitRange)
            MinPosition = LimitRange.Min
            MaxPosition = LimitRange.Max
        
        #STEP 4a: Send Steps command
        self.step("4a")
        await self.send_single_cmd(cmd=Clusters.Objects.ClosureDimension.Commands.Steps(Direction=StepDirectionEnum.TowardsMax, NumberOfSteps=65536), endpoint=self.endpoint)

        #STEP 4b: Wait for motion
        self.step("4b")
        wait_for_motion(self, FullMotionDuration)

        #STEP 4c: Read CurrentPositioning attribute
        self.step("4c")
        currentPositioning = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.CurrentPositioning)

        #Validate values
        asserts.assert_less_equal(currentPositioning.Position, MaxPosition, "Unexpected value")

        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            asserts.assert_not_equal(currentPositioning.Speed, ThreeLevelAutoEnum.Auto, "Unexpected value")
        else:
            asserts.assert_equal(currentPositioning.Speed, ThreeLevelAutoEnum.Auto, "Unexpected value")

        #STEP 4d: Send Steps command
        self.step("4d")
        await self.send_single_cmd(cmd=Clusters.Objects.ClosureDimension.Commands.Steps(Direction=StepDirectionEnum.TowardsMin, NumberOfSteps=2), endpoint=self.endpoint)

        #STEP 4e: Wait for motion
        self.step("4e")
        wait_for_motion(self, StepMotionDuration*2)

        #STEP 4f: Read CurrentPositioning attribute
        self.step("4f")
        currentPositioning = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.CurrentPositioning)

        #Validate values
        expectedPosition = max(MinPosition, MaxPosition - 2*StepValue)
        asserts.assert_equal(currentPositioning.Position, expectedPosition, "Unexpected value")

        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            asserts.assert_not_equal(currentPositioning.Speed, ThreeLevelAutoEnum.Auto, "Unexpected value")
        else:
            asserts.assert_equal(currentPositioning.Speed, ThreeLevelAutoEnum.Auto, "Unexpected value")

        StartPosition = currentPositioning.Position

        #STEP 5a: Send Steps command
        self.step("5a")
        await self.send_single_cmd(cmd=Clusters.Objects.ClosureDimension.Commands.Steps(Direction=StepDirectionEnum.TowardsMax, NumberOfSteps=1), endpoint=self.endpoint)

        #STEP 5b: Read TargetPositioning attribute
        self.step("5b")
        targetPositioning = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.TargetPositioning)

        #Validate values
        asserts.assert_equal(targetPositioning.Position, StartPosition+StepValue, "Unexpected value")

        #STEP 5c: Wait for motion
        self.step("5c")
        wait_for_motion(self, StepMotionDuration)

        #STEP 5d: Read CurrentPositioning attribute
        self.step("5d")
        currentPositioning = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.CurrentPositioning)

        #Validate values
        asserts.assert_equal(currentPositioning.Position, StartPosition+StepValue, "Unexpected value")

        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            asserts.assert_not_equal(currentPositioning.Speed, ThreeLevelAutoEnum.Auto, "Unexpected value")
        else:
            asserts.assert_equal(currentPositioning.Speed, ThreeLevelAutoEnum.Auto, "Unexpected value")

        #STEP 6a: Send Steps command
        self.step("6a")
        await self.send_single_cmd(cmd=Clusters.Objects.ClosureDimension.Commands.Steps(Direction=StepDirectionEnum.TowardsMin, NumberOfSteps=1), endpoint=self.endpoint)

        #STEP 6b: Read TargetPositioning attribute
        self.step("6b")
        targetPositioning = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.TargetPositioning)

        #Validate values
        asserts.assert_equal(targetPositioning.Position, StartPosition, "Unexpected value")

        #STEP 6c: Wait for motion
        self.step("6c")
        wait_for_motion(self, StepMotionDuration)

        #STEP 6d: Read CurrentPositioning attribute
        self.step("6d")
        currentPositioning = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.CurrentPositioning)

        #Validate values
        asserts.assert_equal(currentPositioning.Position, startPosition, "Unexpected value")

        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            asserts.assert_not_equal(currentPositioning.Speed, ThreeLevelAutoEnum.Auto, "Unexpected value")
        else:
            asserts.assert_equal(currentPositioning.Speed, ThreeLevelAutoEnum.Auto, "Unexpected value")

        #STEP 7a: Send Steps command
        self.step("7a")

        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            await self.send_single_cmd(cmd=Clusters.Objects.ClosureDimension.Commands.Steps(Direction=StepDirectionEnum.TowardsMax, NumberOfSteps=1, speed=ThreeLevelAutoEnum.Low), endpoint=self.endpoint)       

        #STEP 7b: Read TargetPositioning attribute
        self.step("7b")
        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            targetPositioning = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.TargetPositioning)

            #Validate values
            asserts.assert_equal(targetPositioning.Position, StartPosition+StepValue, "Unexpected value")
            asserts.assert_equal(targetPositioning.Speed, ThreeLevelAutoEnum.Low, "Unexpected value")

        #STEP 7c: Wait for motion
        self.step("7c")
        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            wait_for_motion(self, StepMotionDuration)

        #STEP 7d: Read CurrentPositioning attribute
        self.step("7d")
        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            currentPositioning = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.CurrentPositioning)

            #Validate values
            asserts.assert_equal(currentPositioning.Position, startPosition+StepValue, "Unexpected value")
            asserts.assert_equal(currentPositioning.Speed, ThreeLevelAutoEnum.Low, "Unexpected value")

        #STEP 8a: Send Steps command
        self.step("8a")

        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            await self.send_single_cmd(cmd=Clusters.Objects.ClosureDimension.Commands.Steps(Direction=StepDirectionEnum.TowardsMin, NumberOfSteps=1, speed=ThreeLevelAutoEnum.Medium), endpoint=self.endpoint)

        #STEP 8b: Read TargetPositioning attribute
        self.step("8b")
        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            targetPositioning = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.TargetPositioning)

            #Validate values
            asserts.assert_equal(targetPositioning.Position, StartPosition, "Unexpected value")
            asserts.assert_equal(targetPositioning.Speed, ThreeLevelAutoEnum.Medium, "Unexpected value")

        #STEP 8c: Wait for motion
        self.step("8c")
        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            wait_for_motion(self, StepMotionDuration)

        #STEP 8d: Read CurrentPositioning attribute
        self.step("8d")
        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            currentPositioning = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.CurrentPositioning)

            #Validate values
            asserts.assert_equal(currentPositioning.Position, startPosition, "Unexpected value")
            asserts.assert_equal(currentPositioning.Speed, ThreeLevelAutoEnum.Medium, "Unexpected value")

        #STEP 9a: Send Steps command
        self.step("9a")

        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            await self.send_single_cmd(cmd=Clusters.Objects.ClosureDimension.Commands.Steps(Direction=StepDirectionEnum.TowardsMax, NumberOfSteps=1, speed=ThreeLevelAutoEnum.High), endpoint=self.endpoint)

        #STEP 9b: Read TargetPositioning attribute
        self.step("9b")
        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            targetPositioning = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.TargetPositioning)

            #Validate values
            asserts.assert_equal(targetPositioning.Position, StartPosition+StepValue, "Unexpected value")
            asserts.assert_equal(targetPositioning.Speed, ThreeLevelAutoEnum.High, "Unexpected value")

        #STEP 9c: Wait for motion
        self.step("9c")
        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            wait_for_motion(self, StepMotionDuration)

        #STEP 9d: Read CurrentPositioning attribute
        self.step("9d")
        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            currentPositioning = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.CurrentPositioning)

            #Validate values
            asserts.assert_equal(currentPositioning.Position, startPosition+StepValue, "Unexpected value")
            asserts.assert_equal(currentPositioning.Speed, ThreeLevelAutoEnum.High, "Unexpected value")

        #STEP 10a: Send Steps command
        self.step("10a")

        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            await self.send_single_cmd(cmd=Clusters.Objects.ClosureDimension.Commands.Steps(Direction=StepDirectionEnum.TowardsMin, NumberOfSteps=1, speed=ThreeLevelAutoEnum.Auto), endpoint=self.endpoint)

        #STEP 10b: Read TargetPositioning attribute
        self.step("10b")
        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            targetPositioning = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.TargetPositioning)

            #Validate values
            asserts.assert_equal(targetPositioning.Position, StartPosition, "Unexpected value")
            asserts.assert_equal(targetPositioning.Speed, ThreeLevelAutoEnum.Auto, "Unexpected value")

        #STEP 10c: Wait for motion
        self.step("10c")
        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            wait_for_motion(self, StepMotionDuration)

        #STEP 10d: Read CurrentPositioning attribute
        self.step("10d")
        if self.pics_guard(self.check_pics("CLDIM.S.F04")):
            currentPositioning = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.CurrentPositioning)

            #Validate values
            asserts.assert_equal(currentPositioning.Position, startPosition, "Unexpected value")
            asserts.assert_not_equal(currentPositioning.Speed, ThreeLevelAutoEnum.Auto, "Unexpected value")


if __name__ == "__main__":
    default_matter_test_main()
