/**
 * Copyright 2020 Alibaba Group Holding Limited.
 *
 * <p>Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file
 * except in compliance with the License. You may obtain a copy of the License at
 *
 * <p>http://www.apache.org/licenses/LICENSE-2.0
 *
 * <p>Unless required by applicable law or agreed to in writing, software distributed under the
 * License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.alibaba.graphscope.groot.schema.ddl;

import com.alibaba.graphscope.groot.operation.Operation;
import com.alibaba.graphscope.groot.operation.ddl.DropVertexTypeOperation;
import com.alibaba.maxgraph.sdkcommon.schema.LabelId;

public class DropVertexTypeExecutor extends AbstractDropTypeExecutor {

    @Override
    protected Operation makeOperation(int partition, long version, LabelId labelId) {
        return new DropVertexTypeOperation(partition, version, labelId);
    }
}
