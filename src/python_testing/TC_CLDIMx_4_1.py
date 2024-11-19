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
import time

import chip.clusters as Clusters
from chip.interaction_model import InteractionModelError, Status
from chip.testing.matter_testing import MatterBaseTest, TestStep, async_test_body, default_matter_test_main
from mobly import asserts

# ==========================
# Enums
# ==========================

LatchingEnum = Clusters.ClosureDimension.Enums.LatchingEnum


class CLDIMx_4_1(MatterBaseTest):
    def __init__(self, *args):
        super().__init__(*args)
        self.endpoint = 0

    def steps_CLDIMx_4_1(self) -> list[TestStep]:
        steps = [
            TestStep(1, "Commissioning, already done", is_commissioning=True),
            TestStep(2, "TH sends Latch command to dut"),
            TestStep(3, "Read TargetLatching attribute"),
            TestStep(4, "Wait for motion"),
            TestStep(5, "Read CurrentLatching attribute"),
            TestStep(6, "TH sends Step command to DUT, with Direction=TowardsMin and NumberOfSteps=1"),
            TestStep(7, "TH sends Unlatch command to dut"),
            TestStep(8, "Read TargetLatching attribute"),
            TestStep(9, "Wait for motion"),
            TestStep(10, "Read CurrentLatching attribute"),
         ]
        return steps
    
    async def read_attribute_expect_success(self, endpoint, attribute):
        cluster = Clusters.Objects.ClosureDimension
        return await self.read_single_attribute_check_success(endpoint=endpoint, cluster=cluster, attribute=attribute)

    async def wait_for_motion(self, duration_s):
        logging.info(f"Test will now wait for {duration_s} seconds")
        time.sleep(duration_s)

    @async_test_body
    async def run_cldim_test_4_1(self, LatchingDuration):
        is_ci = self.check_pics("PICS_SDK_CI_ONLY")

        self.endpoint = self.matter_test_config.endpoint
        
        attributes = Clusters.ClosureDimension.Attributes
        cluster = Clusters.Objects.ClosureDimension

        #STEP 1: Commission DUT to TH (can be skipped if done in a preceding test)
        self.step(1)

        #STEP 2: TH sends Latch command to dut
        self.step(2)
        await self.send_single_cmd(cmd=Clusters.Objects.ClosureDimension.Commands.Latch(), endpoint=self.endpoint)

        #STEP 3: Read TargetLatching attribute
        self.step(3)
        targetLatching = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.TargetLatching)

        #Validate value
        asserts.assert_equal(targetLatching, LatchingEnum.LatchedAndSecured, "Unexpected value")

        #STEP 4: Wait for motion
        self.step(4)
        await self.wait_for_motion(LatchingDuration)

        #STEP 5: Read CurrentLatching attribute
        self.step(5)
        currentLatching = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.CurrentLatching)

        #Validate value
        asserts.assert_equal(currentLatching, LatchingEnum.LatchedAndSecured, "Unexpected value")

        #STEP 6: Send Step command
        self.step(6)
        try: 
            await self.send_single_cmd(cmd=Clusters.Objects.ClosureDimension.Commands.Step(Direction=StepDirectionEnum.TowardsMin, NumberOfSteps=1), endpoint=self.endpoint)
        except InteractionModelError as e:
            asserts.assert_equal(e.status, Status.InvalidInState, "Unexpected error returned")

        #STEP 7: TH sends Unlatch command to dut
        self.step(7)
        await self.send_single_cmd(cmd=Clusters.Objects.ClosureDimension.Commands.Unlatch(), endpoint=self.endpoint)

        #STEP 8: Read TargetLatching attribute
        self.step(8)
        targetLatching = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.TargetLatching)

        #Validate value
        asserts.assert_equal(targetLatching, LatchingEnum.NotLatched, "Unexpected value")

        #STEP 9: Wait for motion
        self.step(9)
        await self.wait_for_motion(LatchingDuration)

        #STEP 10: Read CurrentLatching attribute
        self.step(10)
        currentLatching = await self.read_single_attribute_check_success(endpoint=self.endpoint, cluster=cluster, attribute=attributes.CurrentLatching)

        #Validate value
        asserts.assert_equal(currentLatching, LatchingEnum.NotLatched, "Unexpected value")


class TC_CLDIM1_4_1(MatterBaseTest, CLDIMx_4_1):

    @async_test_body
    async def teardown_test(self):
        await self.teardown()
        return super().teardown_test()

    def setup_class(self):
        return super().setup_class()

    def pics_TC_CLDIM1_4_1(self) -> list[str]:
        return ["CLDIM1.S.F01"]

    @async_test_body
    async def test_TC_CLDIM1_4_1(self):
        await self.run_cldim_test_4_1(LatchingDuration = self.matter_test_config.global_test_params['PIXIT.CLDIM1.LatchingDuration'])

class TC_CLDIM2_4_1(MatterBaseTest, CLDIMx_4_1):

    @async_test_body
    async def teardown_test(self):
        await self.teardown()
        return super().teardown_test()

    def setup_class(self):
        return super().setup_class()

    def pics_TC_CLDIM2_4_1(self) -> list[str]:
        return ["CLDIM2.S.F01"]

    @async_test_body
    async def test_TC_CLDIM2_4_1(self):
        await self.run_cldim_test_4_1(LatchingDuration = self.matter_test_config.global_test_params['PIXIT.CLDIM2.LatchingDuration'])

class TC_CLDIM3_4_1(MatterBaseTest, CLDIMx_4_1):

    @async_test_body
    async def teardown_test(self):
        await self.teardown()
        return super().teardown_test()

    def setup_class(self):
        return super().setup_class()

    def pics_TC_CLDIM3_4_1(self) -> list[str]:
        return ["CLDIM3.S.F01"]

    @async_test_body
    async def test_TC_CLDIM3_4_1(self):
        await self.run_cldim_test_4_1(LatchingDuration = self.matter_test_config.global_test_params['PIXIT.CLDIM3.LatchingDuration'])

class TC_CLDIM4_4_1(MatterBaseTest, CLDIMx_4_1):

    @async_test_body
    async def teardown_test(self):
        await self.teardown()
        return super().teardown_test()

    def setup_class(self):
        return super().setup_class()

    def pics_TC_CLDIM4_4_1(self) -> list[str]:
        return ["CLDIM4.S.F01"]

    @async_test_body
    async def test_TC_CLDIM4_4_1(self):
        await self.run_cldim_test_4_1(LatchingDuration = self.matter_test_config.global_test_params['PIXIT.CLDIM4.LatchingDuration'])

class TC_CLDIM5_4_1(MatterBaseTest, CLDIMx_4_1):

    @async_test_body
    async def teardown_test(self):
        await self.teardown()
        return super().teardown_test()

    def setup_class(self):
        return super().setup_class()

    def pics_TC_CLDIM5_4_1(self) -> list[str]:
        return ["CLDIM5.S.F01"]

    @async_test_body
    async def test_TC_CLDIM5_4_1(self):
        await self.run_cldim_test_4_1(LatchingDuration = self.matter_test_config.global_test_params['PIXIT.CLDIM5.LatchingDuration'])


if __name__ == "__main__":
    default_matter_test_main()
