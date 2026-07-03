<template>
  <div>
    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="filter-row">
          <span class="page-title">数据统计与报表</span>
          <div class="filter-controls">
            <el-button-group>
              <el-button @click="setRange(7)">近7天</el-button>
              <el-button @click="setRange(30)">近30天</el-button>
              <el-button @click="setRange(90)">近90天</el-button>
            </el-button-group>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              class="date-picker-compact"
            />
            <el-button type="primary" @click="loadData">查询</el-button>
          </div>
        </div>
      </template>

      <!-- 概览卡片 -->
      <el-row :gutter="20" style="margin-bottom: 24px">
        <el-col :xs="24" :sm="8">
          <el-card shadow="never" class="stat-card">
            <div class="stat-item">
              <div class="stat-icon" style="background: #dbeafe; color: #2563eb">
                <el-icon size="24"><DataAnalysis /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-label">总预订次数</div>
                <div class="stat-value">{{ totalCount }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-card shadow="never" class="stat-card">
            <div class="stat-item">
              <div class="stat-icon" style="background: #d1fae5; color: #059669">
                <el-icon size="24"><Timer /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-label">总使用时长（小时）</div>
                <div class="stat-value">{{ totalHours }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-card shadow="never" class="stat-card">
            <div class="stat-item">
              <div class="stat-icon" style="background: #fef3c7; color: #d97706">
                <el-icon size="24"><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-label">平均使用率</div>
                <div class="stat-value">{{ avgRate }}%</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 图表区 -->
      <el-row :gutter="20" style="margin-bottom: 24px">
        <el-col :xs="24" :lg="12">
          <el-card shadow="never" class="chart-card">
            <template #header>
              <span class="chart-title">各教室使用率排行</span>
            </template>
            <v-chart class="chart" :option="barOption" autoresize />
          </el-card>
        </el-col>
        <el-col :xs="24" :lg="12">
          <el-card shadow="never" class="chart-card">
            <template #header>
              <span class="chart-title">时段热度分布</span>
            </template>
            <v-chart class="chart" :option="lineOption" autoresize />
          </el-card>
        </el-col>
      </el-row>

      <!-- 明细表格 -->
      <h4 class="section-title">教室使用率明细</h4>
      <el-table :data="usageData" stripe border>
        <el-table-column type="index" label="排名" width="70" align="center" />
        <el-table-column prop="room_no" label="教室" width="100" align="center" />
        <el-table-column prop="floor" label="楼层" width="80" align="center" />
        <el-table-column prop="capacity" label="容量" width="100" align="center" />
        <el-table-column prop="reservation_count" label="预订次数" width="100" align="center" sortable />
        <el-table-column prop="total_hours" label="总时长(小时)" width="130" align="center" sortable />
        <el-table-column prop="usage_rate" label="使用率" width="120" align="center" sortable>
          <template #default="{ row }">
            <el-progress :percentage="Math.min(row.usage_rate, 100)" :color="customColors" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getStatistics } from '@/api/admin'
import { ElMessage } from 'element-plus'
import { DataAnalysis, Timer, TrendCharts } from '@element-plus/icons-vue'

const dateRange = ref([])
const usageData = ref([])
const hotHours = ref([])

const totalCount = computed(() => usageData.value.reduce((sum, item) => sum + item.reservation_count, 0))
const totalHours = computed(() => usageData.value.reduce((sum, item) => sum + item.total_hours, 0).toFixed(2))
const avgRate = computed(() => {
  if (usageData.value.length === 0) return 0
  return (usageData.value.reduce((sum, item) => sum + item.usage_rate, 0) / usageData.value.length).toFixed(2)
})

const customColors = [
  { color: '#059669', percentage: 30 },
  { color: '#d97706', percentage: 60 },
  { color: '#dc2626', percentage: 90 }
]

const barOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', data: usageData.value.map(i => i.room_no), axisLabel: { rotate: 30 } },
  yAxis: { type: 'value', name: '使用率%' },
  series: [{
    data: usageData.value.map(i => i.usage_rate),
    type: 'bar',
    itemStyle: { color: '#2563eb', borderRadius: [4, 4, 0, 0] },
    barWidth: '50%'
  }]
}))

const lineOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', data: hotHours.value.map(i => `${i.hour}:00`), boundaryGap: false },
  yAxis: { type: 'value', name: '预订次数' },
  series: [{
    data: hotHours.value.map(i => i.count),
    type: 'line',
    smooth: true,
    itemStyle: { color: '#059669' },
    areaStyle: { color: 'rgba(5, 150, 105, 0.2)' },
    symbol: 'circle',
    symbolSize: 8
  }]
}))

const setRange = (days) => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - days)
  dateRange.value = [
    start.toISOString().split('T')[0],
    end.toISOString().split('T')[0]
  ]
  loadData()
}

const loadData = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择统计日期范围')
    return
  }
  const res = await getStatistics({
    start_date: dateRange.value[0],
    end_date: dateRange.value[1]
  })
  usageData.value = res.data.usage
  hotHours.value = res.data.hot_hours
}

onMounted(() => {
  setRange(30)
})
</script>

<style scoped>
.filter-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.filter-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}
.date-picker-compact {
  width: 240px;
}
.stat-card {
  border: 1px solid #e2e8f0;
}
.stat-card :deep(.el-card__body) {
  padding: 20px;
}
.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.stat-info {
  flex: 1;
  min-width: 0;
}
.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}
.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #1e293b;
}
.chart-card {
  border: 1px solid #e2e8f0;
}
.chart-card :deep(.el-card__header) {
  padding: 14px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}
.chart {
  width: 100%;
  height: 300px;
}
.section-title {
  margin: 0 0 12px 0;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    align-items: flex-start;
  }
  .filter-controls {
    width: 100%;
  }
  .date-picker-compact {
    width: 100%;
    max-width: 260px;
  }
}
</style>
