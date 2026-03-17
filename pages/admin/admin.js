const STORAGE_KEY = 'mealRecords';

function todayDate() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function thisMonth() {
  return todayDate().slice(0, 7);
}

Page({
  data: {
    dailyDate: todayDate(),
    month: thisMonth(),
    dailyRecords: [],
    monthlyStats: []
  },

  onLoad() {
    this.queryDaily();
    this.queryMonth();
  },

  onShow() {
    this.queryDaily();
    this.queryMonth();
  },

  getRecords() {
    return wx.getStorageSync(STORAGE_KEY) || [];
  },

  onDailyDateChange(e) {
    this.setData({ dailyDate: e.detail.value });
  },

  onMonthChange(e) {
    this.setData({ month: e.detail.value.slice(0, 7) });
  },

  queryDaily() {
    const { dailyDate } = this.data;
    const records = this.getRecords()
      .filter((item) => item.date === dailyDate)
      .sort((a, b) => a.name.localeCompare(b.name, 'zh-Hans-CN'));
    this.setData({ dailyRecords: records });
  },

  queryMonth() {
    const { month } = this.data;
    const records = this.getRecords().filter((item) => item.date.slice(0, 7) === month);

    const countMap = records.reduce((map, item) => {
      map[item.name] = (map[item.name] || 0) + 1;
      return map;
    }, {});

    const monthlyStats = Object.entries(countMap)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name, 'zh-Hans-CN'));

    this.setData({ monthlyStats });
  }
});
