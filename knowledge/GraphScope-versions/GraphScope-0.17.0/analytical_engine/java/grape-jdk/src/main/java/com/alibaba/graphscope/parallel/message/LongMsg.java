/*
 * Copyright 2021 Alibaba Group Holding Limited.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *  	http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.alibaba.graphscope.parallel.message;

import static com.alibaba.graphscope.utils.CppClassName.LONG_MSG;
import static com.alibaba.graphscope.utils.CppHeaderName.CORE_JAVA_JAVA_MESSAGES_H;

import com.alibaba.fastffi.CXXHead;
import com.alibaba.fastffi.FFIFactory;
import com.alibaba.fastffi.FFIGen;
import com.alibaba.fastffi.FFIPointer;
import com.alibaba.fastffi.FFITypeAlias;
import com.alibaba.fastffi.FFITypeFactory;
import com.alibaba.graphscope.utils.JNILibraryName;

/**
 * LongMsg is a java wrapper for <a
 * href="https://github.com/zhanglei1949/GraphScope/blob/main/analytical_engine/core/java/java_messages.h#L33">gs::PrimitiveMessage&lt;double&gt;</a>
 *
 * <p>Grape message manager get message by passing reference, while java passing primitive types or
 * Boxing types in value. So to enabling user passing Long,Double,Int as messages, we provide
 * Wrappers for these primitive types. Feel free to use them in messageManger.
 */
@FFIGen(library = JNILibraryName.JNI_LIBRARY_NAME)
@CXXHead(CORE_JAVA_JAVA_MESSAGES_H)
@FFITypeAlias(LONG_MSG)
public interface LongMsg extends FFIPointer {
    Factory factory = FFITypeFactory.getFactory(Factory.class, LongMsg.class);

    long getData();

    void setData(long value);

    @FFIFactory
    interface Factory {
        /**
         * Create an uninitialized DoubleMsg.
         *
         * @return msg instance.
         */
        LongMsg create();

        /**
         * Create a DoubleMsg with initial value.
         *
         * @param inData input data.
         * @return msg instance.
         */
        LongMsg create(long inData);
    }
}
