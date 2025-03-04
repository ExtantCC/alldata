import request from '@/utils/request'

// datax插件api
export function getList(params) {
  return request({
    url: '/system/api/log/pageList',
    method: 'get',
    params
  })
}

export function clearLog(jobGroup, jobId, type) {
  return request({
    url: '/system/api/log/clearLog?jobGroup=' + jobGroup + '&jobId=' + jobId + '&type=' + type,
    method: 'post'
  })
}

export function killJob(data) {
  return request({
    url: '/system/api/log/killJob',
    method: 'post',
    data
  })
}

export function viewJobLog(executorAddress, triggerTime, logId, fromLineNum) {
  return request({
    url: '/system/api/log/logDetailCat?executorAddress=' + executorAddress + '&triggerTime=' + triggerTime + '&logId=' + logId + '&fromLineNum=' + fromLineNum,
    method: 'get'
  })
}
