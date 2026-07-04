<script setup>
import { ref, onMounted } from 'vue'
import { getUsageStatistics } from '../../api/admin'
import { ElMessage } from 'element-plus'

const dateRange = ref([])
const usageData = ref([])
const hotHours = ref([])
const loading = ref(false)

const fetchStatistics = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择统计日期范围')
    return
  }

  loading.value = true
  try {
    const res = await getUsageStatistics({
      start_date: dateRange.value[0],
      end_date: dateRange.value[1]
    })
    usageData.value = res.data.usage
    hotHours.value = res.data.hot_hours
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const maxCount = ref(0)

onMounted(() => {
  // Default to last 30 days
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  dateRange.value = [
    start.toISOString().split('T')[0],
    end.toISOString().split('T')[0]
  ]
  fetchStatistics()
})
</script>

<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据统计</span>
          <div>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
            />
            <el-button type="primary" class="ml-2" @click="fetchStatistics">查询</el-button>
          </div>
        </div>
      </template>

      <!-- Usage Stats Table -->
      <el-table :data="usageData" v-loading="loading" border class="mb-3">
        <el-table-column prop="room_no" label="教室" width="100" />
        <el-table-column prop="floor" label="楼层" width="80" />
        <el-table-column prop="capacity" label="容量" width="80" />
        <el-table-column prop="reservation_count" label="预订次数" width="100" />
        <el-table-column prop="total_hours" label="使用时长(小时)" width="140" />
        <el-table-column label="使用率">
          <template #default="{ row }">
            <el-progress :percentage="row.usage_rate" />
          </template>
        </el-table-column>
      </el-table>

      <!-- Hot Hours -->
      <el-card v-if="hotHours.length > 0">
        <template #header>
          <span>热门时段分布</span>
        </template>
        <div class="hot-hours">
          <div v-for="item in hotHours" :key="item.hour" class="hour-bar">
            <span class="hour-label">{{ item.hour }}:00</span>
            <el-progress
              :percentage="(item.count / Math.max(...hotHours.map(h => h.count))) * 100"
              :show-text="false"
              :stroke-width="16"
            />
            <span class="hour-count">{{ item.count }}次</span>
          </div>
        </div>
      </el-card>
    </el-card>
  </div>
</template>

<style scoped>
.hot-hours {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.hour-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.hour-label {
  width: 60px;
  text-align: right;
  font-size: 14px;
}

.hour-count {
  width: 60px;
  font-size: 14px;
  color: #606266;
}

.ml-2 {
  margin-left: 10px;
}
</style>
