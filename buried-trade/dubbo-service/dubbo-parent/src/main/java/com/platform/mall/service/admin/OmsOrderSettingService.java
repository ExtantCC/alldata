package com.platform.mall.service.admin;

import com.platform.mall.entity.admin.OmsOrderSetting;

/**
 * 订单设置Service
 * @author AllDataDC
 */
public interface OmsOrderSettingService {
    /**
     * 获取指定订单设置
     */
    OmsOrderSetting getItem(Long id);

    /**
     * 修改指定订单设置
     */
    int update(Long id, OmsOrderSetting orderSetting);
}
